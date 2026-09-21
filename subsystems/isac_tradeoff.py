#!/usr/bin/env python3
"""
Version 6 (Advanced PHY) - Step 6: ISAC Sensing-Communication Tradeoff Analysis
-------------------------------------------------------------------------------------
Analyzes the Pareto optimal boundary between communication channel capacity (Gbps) 
and radar sensing range resolution (cm) across variable subcarrier power/bandwidth
allocations under 140 GHz Sub-THz propagation models.

Author: Abhishek Singh
Repository: 6g-chaotic-superposition-phy
License: MIT
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# System Constants
# =====================================================================
TOTAL_BANDWIDTH = 2.0e9        # 2 GHz Sub-THz Bandwidth
CARRIER_FREQ = 140e9           # 140 GHz Carrier
SPEED_OF_LIGHT = 3e8           # m/s
SNR_OPERATIONAL_DB = 15.0      # Operational SNR

def run_tradeoff_analysis():
    print("=" * 70)
    print("--- Step 6: ISAC Sensing-Communication Tradeoff Analysis ---")
    print("=" * 70)
    
    # Bandwidth allocation fraction for communication (alpha) vs radar (1 - alpha)
    alpha_split = np.linspace(0.1, 0.9, 50)
    
    snr_linear = 10.0 ** (SNR_OPERATIONAL_DB / 10.0)
    
    comm_capacity_gbps = []
    radar_range_res_cm = []
    
    for alpha in alpha_split:
        bw_comm = alpha * TOTAL_BANDWIDTH
        bw_radar = (1.0 - alpha) * TOTAL_BANDWIDTH
        
        # Shannon Capacity (Gbps)
        capacity_bps = bw_comm * np.log2(1.0 + snr_linear)
        comm_capacity_gbps.append(capacity_bps / 1e9)
        
        # Radar Range Resolution (cm) -> Delta_r = c / (2 * B_radar)
        res_m = SPEED_OF_LIGHT / (2.0 * bw_radar)
        radar_range_res_cm.append(res_m * 100.0)
        
    print(f"Total System Bandwidth       : {TOTAL_BANDWIDTH / 1e9:.1f} GHz")
    print(f"Max Communication Rate       : {max(comm_capacity_gbps):.2f} Gbps (at alpha=0.9)")
    print(f"Best Radar Range Resolution  : {min(radar_range_res_cm):.2f} cm (at alpha=0.1)")
    print("=" * 70)
    
    # Visualization
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
    
    # Title & Combined Legend
    plt.title('ISAC Sensing vs Communication Tradeoff Curve (140 GHz, 2 GHz BW)', fontsize=12, pad=12)
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center right')
    
    os.makedirs('docs/images', exist_ok=True)
    plt.tight_layout()
    plt.savefig('docs/images/isac_tradeoff_curve.png', dpi=300)
    print("[SUCCESS] Tradeoff curve plot saved to 'docs/images/isac_tradeoff_curve.png'.")

if __name__ == '__main__':
    run_tradeoff_analysis()
