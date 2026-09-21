import os

# 1. Create necessary directory structure
os.makedirs('subsystems', exist_ok=True)
os.makedirs('docs/images', exist_ok=True)

# 2. Write subsystems/comm_performance.py
comm_code = '''#!/usr/bin/env python3
"""
Version 6 (Advanced PHY) - Step 5: ISAC Communication Performance & BER Evaluation
-------------------------------------------------------------------------------------
Evaluates the communication side of the ISAC waveform by calculating Bit Error Rate
(BER) across varying SNR levels and plotting QPSK constellation degradation.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

NUM_SUBCARRIERS = 1024
NUM_OFDM_SYMBOLS = 128
SNR_DB_RANGE = np.arange(0, 22, 2)

def qpsk_modulate(bits):
    symbols = (1 - 2 * bits[0::2]) + 1j * (1 - 2 * bits[1::2])
    return symbols / np.sqrt(2)

def qpsk_demodulate(symbols):
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
    tx_symbols = qpsk_modulate(tx_bits).reshape((NUM_OFDM_SYMBOLS, NUM_SUBCARRIERS))
    
    ber_results = []
    constellations = {}
    
    for snr_db in SNR_DB_RANGE:
        snr_linear = 10.0 ** (snr_db / 10.0)
        noise_power = 1.0 / snr_linear
        noise = (np.random.normal(0, np.sqrt(noise_power/2), tx_symbols.shape) +
                 1j * np.random.normal(0, np.sqrt(noise_power/2), tx_symbols.shape))
        
        rx_symbols = tx_symbols + noise
        
        if snr_db in [4, 10, 18]:
            constellations[snr_db] = rx_symbols.flatten()[:2000]
            
        rx_bits = qpsk_demodulate(rx_symbols.flatten())
        bit_errors = np.sum(tx_bits != rx_bits)
        ber = bit_errors / total_bits
        ber_results.append(ber)
        
        print(f"SNR: {snr_db:2d} dB | Bit Errors: {bit_errors:5d} / {total_bits} | BER: {ber:.6e}")

    print("=" * 70)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    ax1.semilogy(SNR_DB_RANGE, ber_results, 'bo-', linewidth=2, markersize=6, label='Simulated QPSK ISAC')
    
    from scipy.special import erfc
    snr_linear_range = 10.0 ** (SNR_DB_RANGE / 10.0)
    theoretical_ber = 0.5 * erfc(np.sqrt(snr_linear_range / 2.0))
    ax1.semilogy(SNR_DB_RANGE, theoretical_ber, 'r--', linewidth=1.5, label='Theoretical QPSK')
    
    ax1.set_xlabel('SNR (dB)')
    ax1.set_ylabel('Bit Error Rate (BER)')
    ax1.set_title('ISAC Communication BER Performance')
    ax1.grid(True, which='both', linestyle='--', alpha=0.5)
    ax1.legend()
    
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
    
    plt.tight_layout()
    plt.savefig('docs/images/isac_comm_ber.png', dpi=300)
    print("[SUCCESS] Communication BER plot saved to 'docs/images/isac_comm_ber.png'.")

if __name__ == '__main__':
    run_comm_evaluation()
'''

with open('subsystems/comm_performance.py', 'w') as f:
    f.write(comm_code)

# 3. Write subsystems/isac_tradeoff.py
tradeoff_code = '''#!/usr/bin/env python3
"""
Version 6 (Advanced PHY) - Step 6: ISAC Sensing-Communication Tradeoff Analysis
-------------------------------------------------------------------------------------
Analyzes the Pareto optimal boundary between communication channel capacity (Gbps) 
and radar sensing range resolution (cm).
"""

import os
import numpy as np
import matplotlib.pyplot as plt

TOTAL_BANDWIDTH = 2.0e9        # 2 GHz Sub-THz Bandwidth
CARRIER_FREQ = 140e9           # 140 GHz Carrier
SPEED_OF_LIGHT = 3e8           # m/s
SNR_OPERATIONAL_DB = 15.0      # Operational SNR

def run_tradeoff_analysis():
    print("=" * 70)
    print("--- Step 6: ISAC Sensing-Communication Tradeoff Analysis ---")
    print("=" * 70)
    
    alpha_split = np.linspace(0.1, 0.9, 50)
    snr_linear = 10.0 ** (SNR_OPERATIONAL_DB / 10.0)
    
    comm_capacity_gbps = []
    radar_range_res_cm = []
    
    for alpha in alpha_split:
        bw_comm = alpha * TOTAL_BANDWIDTH
        bw_radar = (1.0 - alpha) * TOTAL_BANDWIDTH
        
        capacity_bps = bw_comm * np.log2(1.0 + snr_linear)
        comm_capacity_gbps.append(capacity_bps / 1e9)
        
        res_m = SPEED_OF_LIGHT / (2.0 * bw_radar)
        radar_range_res_cm.append(res_m * 100.0)
        
    print(f"Total System Bandwidth       : {TOTAL_BANDWIDTH / 1e9:.1f} GHz")
    print(f"Max Communication Rate       : {max(comm_capacity_gbps):.2f} Gbps (at alpha=0.9)")
    print(f"Best Radar Range Resolution  : {min(radar_range_res_cm):.2f} cm (at alpha=0.1)")
    print("=" * 70)
    
    fig, ax1 = plt.subplots(figsize=(8, 5.5))
    
    color_comm = 'tab:blue'
    ax1.set_xlabel('Communication Bandwidth Allocation Fraction (α)', fontsize=11)
    ax1.set_ylabel('Communication Capacity (Gbps)', color=color_comm, fontsize=11)
    line1 = ax1.plot(alpha_split, comm_capacity_gbps, color=color_comm, linewidth=2.5, label='Comm Capacity (Gbps)')
    ax1.tick_params(axis='y', labelcolor=color_comm)
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    ax2 = ax1.twinx()  
    color_radar = 'tab:red'
    ax2.set_ylabel('Radar Range Resolution (cm)', color=color_radar, fontsize=11)
    line2 = ax2.plot(alpha_split, radar_range_res_cm, color=color_radar, linewidth=2.5, linestyle='--', label='Range Res (cm)')
    ax2.tick_params(axis='y', labelcolor=color_radar)
    
    plt.title('ISAC Sensing vs Communication Tradeoff Curve (140 GHz, 2 GHz BW)', fontsize=12, pad=12)
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center right')
    
    plt.tight_layout()
    plt.savefig('docs/images/isac_tradeoff_curve.png', dpi=300)
    print("[SUCCESS] Tradeoff curve plot saved to 'docs/images/isac_tradeoff_curve.png'.")

if __name__ == '__main__':
    run_tradeoff_analysis()
'''

with open('subsystems/isac_tradeoff.py', 'w') as f:
    f.write(tradeoff_code)

# 4. Write run_isac_pipeline.py
orchestrator_code = '''#!/usr/bin/env python3
import sys
import time

def main():
    start_time = time.time()
    print("=" * 80)
    print("      6G ISAC ADVANCED PHY SIMULATION PIPELINE (140 GHz Sub-THz)")
    print("=" * 80)
    
    try:
        from subsystems.comm_performance import run_comm_evaluation
        from subsystems.isac_tradeoff import run_tradeoff_analysis
        
        print("\\n[1/2] Running Communication PHY BER & Constellation Evaluation...")
        run_comm_evaluation()
        
        print("\\n[2/2] Running Sensing-Communication Resource Tradeoff Analysis...")
        run_tradeoff_analysis()
        
        elapsed = time.time() - start_time
        print("\\n" + "=" * 80)
        print(f"[COMPLETE] ISAC PHY Pipeline Executed Successfully in {elapsed:.2f} seconds.")
        print("Generated Artifacts:")
        print("  • docs/images/isac_comm_ber.png")
        print("  • docs/images/isac_tradeoff_curve.png")
        print("=" * 80)
        
    except ImportError as e:
        print(f"\\n[ERROR] Module import failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
'''

with open('run_isac_pipeline.py', 'w') as f:
    f.write(orchestrator_code)

print("[INFO] All local files created successfully.")
