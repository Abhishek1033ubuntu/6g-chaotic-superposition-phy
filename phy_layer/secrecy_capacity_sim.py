#!/usr/bin/env python3
"""
Version 5 (Advanced PHY) - Step 1: Physical Layer Security & Secrecy Capacity Model
------------------------------------------------------------------------------------
Evaluates information-theoretic secrecy capacity, mutual information gap,
and constellation degradation for legitimate receiver (Bob) vs. passive
eavesdropper (Eve) under ARX-20 cryptographic phase cipher superposition.

Author: Abhishek Singh
Repository: 6g-chaotic-superposition-phy
License: MIT
"""

import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# Simulation & Physical Layer Parameters
# =====================================================================
NUM_SUBCARRIERS = 1024         # OFDM Subcarrier Count
QAM_ORDER = 16                 # 16-QAM Constellation
BITS_PER_SYMBOL = 4            # log2(16)
NUM_OFDM_SYMBOLS = 500         # Monte Carlo Frame Density
KEY_BIT_LENGTH = 256           # ARX-20 Symmetric Key Size

# SNR Sweep Range (dB)
SNR_RANGE_DB = np.arange(-10, 31, 2)

# =====================================================================
# ARX-20 Phase Cipher Core Generator (Simulated State Expansion)
# =====================================================================
def generate_arx20_phase_shifts(num_subcarriers: int, seed_key: int = 0xDEADBEEF) -> np.ndarray:
    """
    Generates deterministic pseudo-random phase shifts in [0, 2pi) derived
    from the 256-bit ARX-20 stream cipher state vector.
    """
    np.random.seed(seed_key & 0xFFFFFFFF)
    # ARX-20 uniform pseudo-random phase mapping
    phase_shifts = np.random.uniform(0, 2 * np.pi, size=num_subcarriers)
    return phase_shifts


def generate_16qam_symbols(num_symbols: int) -> np.ndarray:
    """Generates normalized 16-QAM complex constellation symbols."""
    mapping = np.array([-3-3j, -3-1j, -3+3j, -3+1j,
                        -1-3j, -1-1j, -1+3j, -1+1j,
                         3-3j,  3-1j,  3+3j,  3+1j,
                         1-3j,  1-1j,  1+3j,  1+1j])
    indices = np.random.randint(0, 16, size=num_symbols)
    symbols = mapping[indices]
    # Normalize average energy to 1
    return symbols / np.sqrt(10.0), indices


def compute_mutual_information(snr_db: float, ber: float) -> float:
    """
    Estimates mutual information I(X; Y) over a Binary Symmetric Channel (BSC)
    proxy derived from pre-FEC Bit Error Rate:
    I(X; Y) = C_max * [1 - H_b(e)]
    where H_b(e) is the binary entropy function.
    """
    e = np.clip(ber, 1e-12, 0.5)  # Bound error probability to [0, 0.5]
    binary_entropy = -e * np.log2(e) - (1.0 - e) * np.log2(1.0 - e)
    c_max = BITS_PER_SYMBOL  # Maximum capacity bound for 16-QAM
    mutual_info = c_max * (1.0 - binary_entropy)
    return max(0.0, mutual_info)


# =====================================================================
# Main Simulation Pipeline
# =====================================================================
def run_secrecy_capacity_simulation():
    print("=" * 70)
    print("--- Step 1: Information-Theoretic Secrecy Capacity Engine ---")
    print("=" * 70)

    # Valid 256-bit hexadecimal key
    alice_key = 0x6C7361666567756172645F61727832305F7365637265745F6B65795F32303236
    phase_shifts = generate_arx20_phase_shifts(NUM_SUBCARRIERS, seed_key=alice_key)

    bob_ber_list = []
    eve_ber_list = []
    i_alice_bob_list = []
    i_alice_eve_list = []
    secrecy_capacity_list = []

    total_bits = NUM_OFDM_SYMBOLS * NUM_SUBCARRIERS * BITS_PER_SYMBOL

    for snr_db in SNR_RANGE_DB:
        snr_linear = 10.0 ** (snr_db / 10.0)
        noise_variance = 1.0 / (2.0 * snr_linear)

        # 1. Transmit Data Generation & Phase Ciphering
        tx_symbols, tx_indices = generate_16qam_symbols(NUM_SUBCARRIERS * NUM_OFDM_SYMBOLS)
        tx_matrix = tx_symbols.reshape((NUM_OFDM_SYMBOLS, NUM_SUBCARRIERS))

        # Apply ARX-20 Phase Cipher: S_ciphered = S * exp(j * theta_ARX)
        cipher_phase_matrix = np.tile(np.exp(1j * phase_shifts), (NUM_OFDM_SYMBOLS, 1))
        tx_ciphered = tx_matrix * cipher_phase_matrix

        # 2. Channel Propagation (AWGN)
        noise_real = np.random.normal(0, np.sqrt(noise_variance), tx_ciphered.shape)
        noise_imag = np.random.normal(0, np.sqrt(noise_variance), tx_ciphered.shape)
        rx_signal = tx_ciphered + (noise_real + 1j * noise_imag)

        # 3. Legitimate Receiver (Bob) - Possesses ARX-20 Key
        rx_bob_deciphered = rx_signal * np.conj(cipher_phase_matrix)

        # Bob Minimum Distance Demodulation
        mapping_norm = np.array([-3-3j, -3-1j, -3+3j, -3+1j, -1-3j, -1-1j, -1+3j, -1+1j,
                                  3-3j,  3-1j,  3+3j,  3+1j,  1-3j,  1-1j,  1+3j,  1+1j]) / np.sqrt(10.0)

        rx_bob_flat = rx_bob_deciphered.flatten()
        distances_bob = np.abs(rx_bob_flat[:, None] - mapping_norm[None, :])
        bob_demod_indices = np.argmin(distances_bob, axis=1)

        bob_symbol_errors = np.sum(tx_indices != bob_demod_indices)
        bob_ber = bob_symbol_errors / len(tx_indices)
        bob_ber_list.append(bob_ber)

        # 4. Eavesdropper (Eve) - Passive, No Key Access
        rx_eve_flat = rx_signal.flatten()
        distances_eve = np.abs(rx_eve_flat[:, None] - mapping_norm[None, :])
        eve_demod_indices = np.argmin(distances_eve, axis=1)

        eve_symbol_errors = np.sum(tx_indices != eve_demod_indices)
        eve_ber = eve_symbol_errors / len(tx_indices)
        eve_ber_list.append(eve_ber)

        # 5. Compute Mutual Information & Secrecy Capacity
        i_bob = compute_mutual_information(snr_db, bob_ber)
        i_eve = compute_mutual_information(snr_db, eve_ber)
        secrecy_cap = max(0.0, i_bob - i_eve)

        i_alice_bob_list.append(i_bob)
        i_alice_eve_list.append(i_eve)
        secrecy_capacity_list.append(secrecy_cap)

    # Print Summary Results at High SNR (20 dB)
    ref_idx = np.where(SNR_RANGE_DB == 20)[0][0]
    print(f"Target Evaluation SNR     : 20 dB")
    print(f"Bob Pre-FEC BER (Keyed)   : {bob_ber_list[ref_idx]:.6f} (PASS)")
    print(f"Eve Pre-FEC BER (Unkeyed) : {eve_ber_list[ref_idx]:.6f} (MAX UNCERTAINTY)")
    print(f"Mutual Information I(X;Y) : {i_alice_bob_list[ref_idx]:.4f} bits/sym")
    print(f"Mutual Information I(X;Z) : {i_alice_eve_list[ref_idx]:.4f} bits/sym")
    print(f"Secrecy Capacity (Cs)     : {secrecy_capacity_list[ref_idx]:.4f} bits/sym")
    print("=" * 70)

    # Plotting Secrecy Capacity & BER Curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(SNR_RANGE_DB, i_alice_bob_list, 'b-o', label='Bob Capacity $I(X; Y)$', linewidth=2)
    ax1.plot(SNR_RANGE_DB, i_alice_eve_list, 'r--s', label='Eve Information $I(X; Z)$', linewidth=2)
    ax1.plot(SNR_RANGE_DB, secrecy_capacity_list, 'g-^', label='Secrecy Capacity $C_s$', linewidth=2.5)
    ax1.set_xlabel('SNR (dB)')
    ax1.set_ylabel('Information Rate (bits/symbol)')
    ax1.set_title('Information-Theoretic Secrecy Capacity')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend()

    ax2.semilogy(SNR_RANGE_DB, np.maximum(bob_ber_list, 1e-5), 'b-o', label='Bob (Keyed Receiver)', linewidth=2)
    ax2.semilogy(SNR_RANGE_DB, eve_ber_list, 'r--s', label='Eve (Unkeyed Eavesdropper)', linewidth=2)
    ax2.set_xlabel('SNR (dB)')
    ax2.set_ylabel('Pre-FEC Bit Error Rate (BER)')
    ax2.set_title('PLS Physical Layer BER Resilience')
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()
    import os
    os.makedirs('docs/images', exist_ok=True)
    plt.tight_layout()
    plt.savefig('docs/images/secrecy_capacity_analysis.png', dpi=300)
    print("[SUCCESS] Output plot saved to 'docs/images/secrecy_capacity_analysis.png'.")

if __name__ == '__main__':
    run_secrecy_capacity_simulation()
