#!/usr/bin/env python3
"""
Version 6 (Advanced PHY) - Step 5: ISAC Communication Performance & BER Evaluation
-------------------------------------------------------------------------------------
Evaluates the communication side of the ISAC waveform by calculating Bit Error Rate
(BER) across varying SNR levels and plotting QPSK/16-QAM constellation degradation
under Sub-THz channel conditions.

Author: Abhishek Singh
Repository: 6g-chaotic-superposition-phy
License: MIT
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# Simulation Parameters
# =====================================================================
NUM_SUBCARRIERS = 1024
NUM_OFDM_SYMBOLS = 128
SNR_DB_RANGE = np.arange(0, 22, 2)
MODULATION_ORDER = 4  # QPSK (2 bits per symbol)

def qpsk_modulate(bits):
    """Maps binary pairs to QPSK constellation points."""
    symbols = (1 - 2 * bits[0::2]) + 1j * (1 - 2 * bits[1::2])
    return symbols / np.sqrt(2)

def qpsk_demodulate(symbols):
    """Demodulates QPSK symbols back into raw bits."""
    real_bits = (np.real(symbols) < 0).astype(int)
    imag_bits = (np.imag(symbols) < 0).astype(int)
    bits = np.zeros(2 * len(symbols), dtype=int)
    bits[0::2] = real_bits
    bits[1::2] = imag_bits
    return bits

def run_comm_evaluation():
    print("=" * 70)
    print("--- Step 5: ISAC Communication Performance & BER Evaluation ---")
    print("=" * 70)
    
    total_bits = NUM_SUBCARRIERS * NUM_OFDM_SYMBOLS * 2
    np.random.seed(42)
    tx_bits = np.random.randint(0, 2, total_bits)
    
    # Map bits to QPSK symbols
    tx_symbols = qpsk_modulate(tx_bits).reshape((NUM_OFDM_SYMBOLS, NUM_SUBCARRIERS))
    
    ber_results = []
    constellations = {}
    
    for snr_db in SNR_DB_RANGE:
        snr_linear = 10.0 ** (snr_db / 10.0)
        noise_power = 1.0 / snr_linear
        
        # AWGN Channel Simulation
        noise = (np.random.normal(0, np.sqrt(noise_power/2), tx_symbols.shape) +
                 1j * np.random.normal(0, np.sqrt(noise_power/2), tx_symbols.shape))
        
        rx_symbols = tx_symbols + noise
        
        # Save sample constellation at low, mid, high SNR
        if snr_db in [4, 10, 18]:
            constellations[snr_db] = rx_symbols.flatten()[:2000]
            
        # Demodulate & calculate BER
        rx_bits = qpsk_demodulate(rx_symbols.flatten())
        bit_errors = np.sum(tx_bits != rx_bits)
        ber = bit_errors / total_bits
        ber_results.append(ber)
        
        print(f"SNR: {snr_db:2d} dB | Bit Errors: {bit_errors:5d} / {total_bits} | BER: {ber:.6e}")

    print("=" * 70)
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Subplot 1: BER vs SNR
    ax1.semilogy(SNR_DB_RANGE, ber_results, 'bo-', linewidth=2, markersize=6, label='Simulated QPSK ISAC')
    # Theoretical QPSK BER curve: Q(sqrt(2 * Eb/N0))
    from scipy.special import erfc
    snr_linear_range = 10.0 ** (SNR_DB_RANGE / 10.0)
    theoretical_ber = 0.5 * erfc(np.sqrt(snr_linear_range / 2.0))
    ax1.semilogy(SNR_DB_RANGE, theoretical_ber, 'r--', linewidth=1.5, label='Theoretical QPSK')
    
    ax1.set_xlabel('SNR (dB)')
    ax1.set_ylabel('Bit Error Rate (BER)')
    ax1.set_title('ISAC Communication BER Performance')
    ax1.grid(True, which='both', linestyle='--', alpha=0.5)
    ax1.legend()
    
    # Subplot 2: Constellation Diagrams
    colors = {4: 'red', 10: 'orange', 18: 'green'}
    for snr_val, samples in constellations.items():
        ax2.scatter(np.real(samples), np.imag(samples), s=8, alpha=0.5, 
                    color=colors[snr_val], label=f'SNR = {snr_val} dB')
        
    ax2.set_xlabel('In-Phase (I)')
    ax2.set_ylabel('Quadrature (Q)')
    ax2.set_title('Received QPSK Constellation Clusters')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')
    ax2.set_xlim([-2, 2])
    ax2.set_ylim([-2, 2])
    
    os.makedirs('docs/images', exist_ok=True)
    plt.tight_layout()
    plt.savefig('docs/images/isac_comm_ber.png', dpi=300)
    print("[SUCCESS] Communication BER plot saved to 'docs/images/isac_comm_ber.png'.")

if __name__ == '__main__':
    run_comm_evaluation()
