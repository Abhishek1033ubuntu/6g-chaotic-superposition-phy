#!/usr/bin/env python3
"""
Version 5 (Advanced PHY) - Step 2: ISAC Delay-Doppler Ambiguity Matrix
----------------------------------------------------------------------
Computes the 2D Delay-Doppler Ambiguity Function |chi(tau, nu)| for the
ARX-20 phase-coded OFDM waveform with high-density oversampling.

Author: Abhishek Singh
Repository: 6g-chaotic-superposition-phy
License: MIT
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# System Parameters
# =====================================================================
NUM_SUBCARRIERS = 1024         # Subcarrier Count (N)
SUBCARRIER_SPACING = 960e3     # 960 kHz SCS
CARRIER_FREQ = 140e9           # 140 GHz Sub-THz
SPEED_OF_LIGHT = 3e8           # m/s

BANDWIDTH = NUM_SUBCARRIERS * SUBCARRIER_SPACING  # ~983.04 MHz
SYMBOL_DURATION = 1.0 / SUBCARRIER_SPACING        # ~1.0417 microseconds

# =====================================================================
# Ambiguity Core with High-Density Sampling
# =====================================================================
def generate_arx20_phase_shifts(num_subcarriers: int, key: int = 0x6C736166) -> np.ndarray:
    np.random.seed(key & 0xFFFFFFFF)
    return np.random.uniform(0, 2 * np.pi, size=num_subcarriers)


def compute_ambiguity_matrix(range_window_m: float = 3.0, num_range_bins: int = 1024, num_doppler_bins: int = 128, use_windowing: bool = True):
    """
    Computes Ambiguity Function over a focused, highly oversampled delay grid
    to avoid grid-sampling aliasing on high-bandwidth mainlobes.
    """
    key = 0x6C7361666567756172645F61727832305F7365637265745F6B65795F32303236
    phase_shifts = generate_arx20_phase_shifts(NUM_SUBCARRIERS, key=key)
    subcarriers = np.exp(1j * phase_shifts)

    if use_windowing:
        window = np.hanning(NUM_SUBCARRIERS)
        # Normalize window power
        window /= np.sqrt(np.mean(window**2))
        subcarriers = subcarriers * window

    time_grid = np.linspace(0, SYMBOL_DURATION, NUM_SUBCARRIERS)
    
    # Focused delay grid around center: +/- range_window_m
    max_tau = (2.0 * range_window_m) / SPEED_OF_LIGHT
    delay_vec = np.linspace(-max_tau, max_tau, num_range_bins)
    doppler_vec = np.linspace(-2e4, 2e4, num_doppler_bins)

    ambiguity_map = np.zeros((num_doppler_bins, num_range_bins))

    # Vectorized computation across delays
    k_vec = np.arange(NUM_SUBCARRIERS)
    for i, nu in enumerate(doppler_vec):
        doppler_mod = np.exp(1j * 2 * np.pi * nu * time_grid)
        s_doppler = subcarriers * doppler_mod
        
        # Matrix phase shift: (N_subcarriers, N_delays)
        delay_phases = np.exp(-1j * 2 * np.pi * SUBCARRIER_SPACING * np.outer(k_vec, delay_vec))
        s_delayed_matrix = subcarriers[:, None] * delay_phases
        
        # Cross correlation across all delays
        ambiguity_map[i, :] = np.abs(np.vdot(s_doppler, s_delayed_matrix) if False else np.abs(np.dot(s_doppler.conj(), s_delayed_matrix)))

    peak_val = np.max(ambiguity_map)
    if peak_val > 0:
        ambiguity_map /= peak_val

    return delay_vec, doppler_vec, ambiguity_map


def compute_crlb_range(snr_db: float, bandwidth: float) -> float:
    snr_linear = 10.0 ** (snr_db / 10.0)
    effective_gabor_bw = bandwidth / np.sqrt(12)
    crlb_var = (SPEED_OF_LIGHT ** 2) / (8 * (np.pi ** 2) * snr_linear * (effective_gabor_bw ** 2))
    return np.sqrt(crlb_var)


# =====================================================================
# Execution Pipeline
# =====================================================================
def run_ambiguity_simulation():
    print("=" * 70)
    print("--- Step 2: ISAC Delay-Doppler Ambiguity & CRLB Matrix ---")
    print("=" * 70)

    # 1. Compute oversampled ambiguity matrix within +/- 3.0 m window (1024 bins = ~0.58 cm per bin)
    use_win = True
    delay_vec, doppler_vec, amb_matrix = compute_ambiguity_matrix(
        range_window_m=3.0, 
        num_range_bins=1024, 
        num_doppler_bins=128, 
        use_windowing=use_win
    )

    range_grid = (delay_vec * SPEED_OF_LIGHT) / 2.0  # meters
    velocity_grid = (doppler_vec * SPEED_OF_LIGHT / CARRIER_FREQ) * 3.6  # km/h
    amb_db = 20 * np.log10(np.maximum(amb_matrix, 1e-4))

    zero_doppler_idx = np.argmin(np.abs(velocity_grid))
    range_profile_db = amb_db[zero_doppler_idx, :]

    # Accurate Peak Sidelobe Extraction (exclude mainlobe region |R| < 0.35m)
    mainlobe_mask = np.abs(range_grid) < 0.35
    sidelobe_profile = np.copy(range_profile_db)
    sidelobe_profile[mainlobe_mask] = -100.0
    pslr_db = np.max(sidelobe_profile)

    crlb_range_m = compute_crlb_range(15.0, BANDWIDTH)
    actual_range_res_m = SPEED_OF_LIGHT / (2 * BANDWIDTH)

    print(f"System Operational SCS   : {SUBCARRIER_SPACING / 1e3:.0f} kHz")
    print(f"Effective Bandwidth      : {BANDWIDTH / 1e6:.2f} MHz")
    print(f"Theoretical Range Res    : {actual_range_res_m * 100:.2f} cm")
    print(f"CRLB Range Error (15 dB) : {crlb_range_m * 100:.2f} cm")
    print(f"Peak-to-Sidelobe (PSLR)  : {pslr_db:.2f} dB ({'PASS' if pslr_db < -13.0 else 'FAIL'})")
    print("=" * 70)

    # Plot generation
    fig = plt.figure(figsize=(13, 5))

    # Subplot 1: 2D Ambiguity Contour (Focused View)
    ax1 = fig.add_subplot(1, 2, 1)
    mesh = ax1.pcolormesh(range_grid, velocity_grid, amb_db, cmap='viridis', shading='auto', vmin=-35, vmax=0)
    fig.colorbar(mesh, ax=ax1, label='Ambiguity Level (dB)')
    ax1.set_xlabel('Range Delay Offset (m)')
    ax1.set_ylabel('Doppler Velocity (km/h)')
    ax1.set_title('ARX-20 OFDM Ambiguity Function |$\\chi(\\tau, \\nu)$|')
    ax1.grid(True, linestyle='--', alpha=0.4)

    # Subplot 2: Range Cut with Smooth Continuous Roll-Off
    ax2 = fig.add_subplot(1, 2, 2)
    label_str = 'Hann Windowed Profile' if use_win else 'Unwindowed Profile'
    ax2.plot(range_grid, range_profile_db, 'b-', linewidth=2, label=label_str)
    ax2.axhline(pslr_db, color='r', linestyle='--', label=f'Peak Sidelobe ({pslr_db:.2f} dB)')
    ax2.set_xlim([-2.0, 2.0])  # +/- 2m gives a crisp view of mainlobe + first 4 sidelobes
    ax2.set_ylim([-40, 2])
    ax2.set_xlabel('Range Offset (m)')
    ax2.set_ylabel('Normalized Power (dB)')
    ax2.set_title('Zero-Doppler Range Profile (Oversampled)')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(loc='upper right')

    os.makedirs('docs/images', exist_ok=True)
    plt.tight_layout()
    plt.savefig('docs/images/isac_ambiguity_matrix.png', dpi=300)
    print("[SUCCESS] Output plot saved to 'docs/images/isac_ambiguity_matrix.png'.")

if __name__ == '__main__':
    run_ambiguity_simulation()
