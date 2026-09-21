#!/usr, bin/env python3
"""
Version 6 (Advanced PHY) - Step 3: Multi-Target ISAC Range-Doppler & OS-CFAR Processing
-------------------------------------------------------------------------------------
Simulates a multi-target radar environment using the ARX-20 phase-coded ISAC waveform,
performs 2D Range-Doppler processing, and executes 2D Ordered-Statistic CFAR (OS-CFAR)
target detection to eliminate target masking in dense multi-target scenarios.

Author: Abhishek Singh
Repository: 6g-chaotic-superposition-phy
License: MIT
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# Radar & Physical Parameters
# =====================================================================
NUM_SUBCARRIERS = 1024         # Fast-time Range Bins (N_k)
NUM_OFDM_SYMBOLS = 128         # Slow-time Doppler Bins (N_l)
DOPPLER_FFT_SIZE = 512         # Zero-padded Slow-Time FFT size
SUBCARRIER_SPACING = 960e3     # 960 kHz Subcarrier Spacing (SCS)
CARRIER_FREQ = 140e9           # 140 GHz Sub-THz Carrier
SPEED_OF_LIGHT = 3e8           # m/s

BANDWIDTH = NUM_SUBCARRIERS * SUBCARRIER_SPACING   # ~983.04 MHz
SYMBOL_DURATION = 1.0 / SUBCARRIER_SPACING         # ~1.0417 microseconds
PRI = SYMBOL_DURATION                              # Pulse Repetition Interval

# =====================================================================
# Target Environment Definition
# =====================================================================
TARGETS = [
    {"range_m": 12.5, "velocity_kmh": 45.0,  "rcs_db": 10.0},  # Primary target
    {"range_m": 28.0, "velocity_kmh": -80.0, "rcs_db": 15.0},  # Approaching target (Negative Velocity)
    {"range_m": 13.2, "velocity_kmh": 48.0,  "rcs_db": 6.0}    # Close-in weaker target
]

# =====================================================================
# 2D OS-CFAR Detector Core (Ordered Statistic CFAR)
# =====================================================================
def os_cfar_2d(rd_matrix_db, guard_cells=(1, 1), training_cells=(4, 4), k_rank_ratio=0.75, scale_factor=2.2, min_power_db=-35.0):
    """
    2D Ordered-Statistic CFAR (OS-CFAR) Detector.
    Sorts surrounding training cells to prevent adjacent strong targets from masking weaker targets.
    """
    num_doppler, num_range = rd_matrix_db.shape
    rd_linear = 10.0 ** (rd_matrix_db / 10.0)
    
    gr, gd = guard_cells
    tr, td = training_cells
    
    total_window_cells = (2 * (tr + gr) + 1) * (2 * (td + gd) + 1)
    guard_window_cells = (2 * gr + 1) * (2 * gd + 1)
    num_train_cells = total_window_cells - guard_window_cells
    
    # Rank index for order statistics (e.g., 75th percentile)
    k_rank = int(np.floor(k_rank_ratio * num_train_cells))
    
    detections_mask = np.zeros_like(rd_matrix_db, dtype=bool)
    threshold_map = np.full_like(rd_matrix_db, -100.0)
    
    for d_idx in range(td + gd, num_doppler - (td + gd)):
        for r_idx in range(tr + gr, num_range - (tr + gr)):
            # Absolute noise floor squelch check
            if rd_matrix_db[d_idx, r_idx] < min_power_db:
                continue

            window = rd_linear[
                d_idx - (td + gd): d_idx + (td + gd) + 1,
                r_idx - (tr + gr): r_idx + (tr + gr) + 1
            ]
            
            train_mask = np.ones(window.shape, dtype=bool)
            train_mask[td:td + 2*gd + 1, tr:tr + 2*gr + 1] = False
            
            # Order statistics: Sort reference cells and select the k-th rank element
            sorted_train_cells = np.sort(window[train_mask])
            noise_rank_power = sorted_train_cells[k_rank]
            
            thresh_linear = scale_factor * noise_rank_power
            threshold_map[d_idx, r_idx] = 10.0 * np.log10(thresh_linear)
            
            if rd_linear[d_idx, r_idx] > thresh_linear:
                detections_mask[d_idx, r_idx] = True
                
    return detections_mask, threshold_map


def cluster_detections(detections_mask, rd_power_db, neighborhood=2):
    """Suppresses non-maximum adjacent detections to isolate distinct target peaks."""
    det_d, det_r = np.where(detections_mask)
    clustered_mask = np.zeros_like(detections_mask, dtype=bool)
    
    num_d, num_r = detections_mask.shape
    for d, r in zip(det_d, det_r):
        d_min, d_max = max(0, d - neighborhood), min(num_d, d + neighborhood + 1)
        r_min, r_max = max(0, r - neighborhood), min(num_r, r + neighborhood + 1)
        
        local_region = rd_power_db[d_min:d_max, r_min:r_max]
        if rd_power_db[d, r] == np.max(local_region):
            clustered_mask[d, r] = True
            
    return clustered_mask

# =====================================================================
# Main Execution Pipeline
# =====================================================================
def run_target_detection():
    print("=" * 70)
    print("--- Step 3: Multi-Target ISAC Range-Doppler & OS-CFAR Processing ---")
    print("=" * 70)
    
    # 1. Transmit Frame Generation
    np.random.seed(42)
    tx_frame = np.exp(1j * np.random.uniform(0, 2*np.pi, (NUM_OFDM_SYMBOLS, NUM_SUBCARRIERS)))
    
    # Apply Blackman window across subcarriers (Fast-time)
    win_freq = np.blackman(NUM_SUBCARRIERS)
    tx_frame_windowed = tx_frame * win_freq[None, :]
    
    rx_frame = np.zeros_like(tx_frame_windowed, dtype=complex)
    
    # 2. Target Echo Signal Superposition
    k_indices = np.arange(NUM_SUBCARRIERS)
    l_indices = np.arange(NUM_OFDM_SYMBOLS)
    
    for tgt in TARGETS:
        tau = (2.0 * tgt["range_m"]) / SPEED_OF_LIGHT
        v_ms = tgt["velocity_kmh"] / 3.6
        f_d = (2.0 * v_ms * CARRIER_FREQ) / SPEED_OF_LIGHT
        amp = 10.0 ** (tgt["rcs_db"] / 20.0)
        
        delay_phase = np.exp(-1j * 2 * np.pi * k_indices * SUBCARRIER_SPACING * tau)
        doppler_phase = np.exp(1j * 2 * np.pi * f_d * l_indices * PRI)
        
        rx_frame += amp * (tx_frame_windowed * delay_phase[None, :]) * doppler_phase[:, None]
        
    # Thermal Noise Addition (AWGN)
    snr_noise_db = 10.0
    noise_power = 10.0 ** (-snr_noise_db / 10.0)
    noise = (np.random.normal(0, np.sqrt(noise_power/2), rx_frame.shape) + 
             1j * np.random.normal(0, np.sqrt(noise_power/2), rx_frame.shape))
    rx_frame += noise
    
    # 3. Channel Estimation & 2D Range-Doppler Processing
    channel_matrix = rx_frame / tx_frame
    
    # Fast-Time IFFT (Range)
    range_profile_matrix = np.fft.ifft(channel_matrix, axis=1)
    
    # Apply Blackman Window along Slow-Time
    win_doppler = np.blackman(NUM_OFDM_SYMBOLS)
    range_profile_windowed = range_profile_matrix * win_doppler[:, None]
    
    # Slow-Time FFT with Zero-Padding (Doppler)
    rd_map = np.fft.fftshift(np.fft.fft(range_profile_windowed, n=DOPPLER_FFT_SIZE, axis=0), axes=0)
    
    rd_power_linear = np.abs(rd_map)**2
    rd_power_db = 10 * np.log10(rd_power_linear / np.max(rd_power_linear))
    
    # Physical Axis Calculation
    range_grid = (np.arange(NUM_SUBCARRIERS) * SPEED_OF_LIGHT) / (2.0 * BANDWIDTH)
    doppler_freqs = np.fft.fftshift(np.fft.fftfreq(DOPPLER_FFT_SIZE, d=PRI))
    velocity_grid = (doppler_freqs * SPEED_OF_LIGHT / (2.0 * CARRIER_FREQ)) * 3.6
    
    # 4. 2D OS-CFAR Processing & Peak Clustering
    raw_detections, threshold_map = os_cfar_2d(
        rd_power_db, guard_cells=(1, 1), training_cells=(4, 4), k_rank_ratio=0.75, scale_factor=2.2, min_power_db=-35.0
    )
    clustered_detections = cluster_detections(raw_detections, rd_power_db, neighborhood=2)
    
    det_d_indices, det_r_indices = np.where(clustered_detections)
    
    print(f"Total Targets Injected  : {len(TARGETS)}")
    print(f"Clustered CFAR Count    : {len(det_r_indices)}")
    print("-" * 70)
    print("Detected Target Parameters:")
    for idx, (d_i, r_i) in enumerate(zip(det_d_indices, det_r_indices)):
        print(f" Target #{idx+1}: Range = {range_grid[r_i]:.2f} m | Velocity = {velocity_grid[d_i]:.2f} km/h | Power = {rd_power_db[d_i, r_i]:.1f} dB")
    print("=" * 70)
    
    # 5. Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Subplot 1: 2D Range-Doppler Heatmap
    mesh = ax1.pcolormesh(range_grid, velocity_grid, rd_power_db, cmap='jet', shading='auto', vmin=-45, vmax=0)
    fig.colorbar(mesh, ax=ax1, label='Normalized Power (dB)')
    ax1.set_xlim([0, 40])
    ax1.set_ylim([-150, 150])
    ax1.set_xlabel('Range (m)')
    ax1.set_ylabel('Velocity (km/h)')
    ax1.set_title('ISAC Range-Doppler Radar Map')
    ax1.grid(True, linestyle='--', alpha=0.4)
    
    # Overlay OS-CFAR Detections
    if len(det_r_indices) > 0:
        ax1.scatter(range_grid[det_r_indices], velocity_grid[det_d_indices], 
                    edgecolor='white', facecolor='none', s=140, linewidths=2.0, label='OS-CFAR Detections')
        ax1.legend(loc='upper right')
        
    # Subplot 2: 1D Range Cut at Target Velocity (v ~ 45 km/h)
    target_v_idx = np.argmin(np.abs(velocity_grid - 45.0))
    ax2.plot(range_grid, rd_power_db[target_v_idx, :], 'b-', linewidth=1.5, label='Range Cut (v ~ 45 km/h)')
    ax2.plot(range_grid, threshold_map[target_v_idx, :], 'r--', linewidth=1.5, label='OS-CFAR Threshold')
    ax2.set_xlim([0, 40])
    ax2.set_ylim([-50, 5])
    ax2.set_xlabel('Range (m)')
    ax2.set_ylabel('Power (dB)')
    ax2.set_title('1D Range Profile vs OS-CFAR Threshold')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')
    
    os.makedirs('docs/images', exist_ok=True)
    plt.tight_layout()
    plt.savefig('docs/images/isac_target_detection.png', dpi=300)
    print("[SUCCESS] Output plot saved to 'docs/images/isac_target_detection.png'.")

if __name__ == '__main__':
    run_target_detection()
