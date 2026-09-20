#!/usr/bin/env python3
"""
Version 2: Single-Axis Spatial Steering & Street Canyon Propagation Model
-------------------------------------------------------------------------
Simulates mmWave street canyon propagation (3GPP TR 38.901 UMi Street Canyon),
single-axis horizontal beam steering toward shadow corridors, and vertical
aperture insertion/reflection losses.

Author: Abhishek Singh
Repository: 6g-chaotic-superposition-phy
License: MIT
"""

import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# Simulation Parameters
# =====================================================================
CARRIER_FREQ_GHZ = 28.0       # Carrier Frequency in GHz
C_LIGHT = 3.0e8               # Speed of light (m/s)
WAVELENGTH = C_LIGHT / (CARRIER_FREQ_GHZ * 1e9)

# Street Canyon Geometry
CANYON_WIDTH_M = 30.0         # Width of street canyon between buildings (meters)
CANYON_LENGTH_M = 200.0       # Length of simulated street corridor (meters)
GNB_TX_HEIGHT_M = 10.0        # Tx Base Station height (meters)
UE_RX_HEIGHT_M = 1.5          # Rx User Equipment height (meters)

# Link Budget & RF Specs
TX_POWER_DBM = 30.0           # Tx Transmit Power (dBm)
TX_ANT_GAIN_DBI = 15.0        # Tx Array Gain (dBi)
RX_ANT_GAIN_DBI = 5.0         # Rx Antenna Gain (dBi)
APERTURE_INSERTION_LOSS_DB = 1.8  # Vertical aperture loss (<= 2.0 dB)
BUILDING_REFLECT_COEFF = 0.65 # Reflection coefficient for concrete facade

# =====================================================================
# Path Loss & Steering Functions
# =====================================================================
def compute_3gpp_umi_los_path_loss(distance_3d: np.ndarray, f_ghz: float) -> np.ndarray:
    """
    Computes 3GPP TR 38.901 UMi (Urban Micro) Line-of-Sight Path Loss.
    PL_UMi_LOS = 32.4 + 21.0 * log10(d3D) + 20.0 * log10(fc)
    """
    d3d_clamped = np.maximum(distance_3d, 1.0)
    pl_db = 32.4 + 21.0 * np.log10(d3d_clamped) + 20.0 * np.log10(f_ghz)
    return pl_db


def compute_single_axis_steering_gain(steering_angle_deg: float, target_angle_deg: np.ndarray) -> np.ndarray:
    """
    Calculates single-axis horizontal beamsteering gain envelope (sinc profile).
    """
    angle_diff_rad = np.radians(target_angle_deg - steering_angle_deg)
    array_factor = np.sinc(2.0 * np.sin(angle_diff_rad) / WAVELENGTH)
    gain_linear = np.abs(array_factor) ** 2
    gain_db = 10.0 * np.log10(np.maximum(gain_linear, 1e-4))  # -40 dB floor
    return gain_db


def run_street_canyon_simulation():
    print("=" * 65)
    print("--- Version 2: Single-Axis Spatial Steering Canyon Simulation ---")
    print("=" * 65)

    # Spatial Grid across the street canyon
    x_coords = np.linspace(0.5, CANYON_WIDTH_M - 0.5, 60)      # Across street width
    y_coords = np.linspace(1.0, CANYON_LENGTH_M, 200)          # Down street length
    X, Y = np.meshgrid(x_coords, y_coords)

    # Tx gNB Position (Centered at street entrance)
    tx_pos = np.array([CANYON_WIDTH_M / 2.0, 0.0, GNB_TX_HEIGHT_M])

    # Calculate 3D Distances
    dist_3d = np.sqrt((X - tx_pos[0])**2 + (Y - tx_pos[1])**2 + (UE_RX_HEIGHT_M - tx_pos[2])**2)
    angles_deg = np.degrees(np.arctan2(X - tx_pos[0], Y - tx_pos[1]))

    # Baseline 3GPP Path Loss & Received Power (Unassisted)
    pl_baseline = compute_3gpp_umi_los_path_loss(dist_3d, CARRIER_FREQ_GHZ)
    rx_power_baseline = TX_POWER_DBM + TX_ANT_GAIN_DBI + RX_ANT_GAIN_DBI - pl_baseline

    # Single-Axis Beam Steering (Steered along canyon axis +15 degrees to shadow forwarding)
    steering_angle = 15.0
    steering_gain = compute_single_axis_steering_gain(steering_angle, angles_deg)

    # Assisted Received Power with Single-Axis Reflection/Forwarding
    rx_power_assisted = (
        TX_POWER_DBM 
        + TX_ANT_GAIN_DBI 
        + RX_ANT_GAIN_DBI 
        + steering_gain 
        - pl_baseline 
        - APERTURE_INSERTION_LOSS_DB
    )

    # Coverage Metrics (Sensitivity Threshold: -75 dBm)
    threshold_dbm = -75.0
    cov_baseline = np.mean(rx_power_baseline >= threshold_dbm) * 100.0
    cov_assisted = np.mean(rx_power_assisted >= threshold_dbm) * 100.0

    print(f"Carrier Frequency         : {CARRIER_FREQ_GHZ} GHz")
    print(f"Canyon Dimensions         : {CANYON_WIDTH_M}m (W) x {CANYON_LENGTH_M}m (L)")
    print(f"Vertical Aperture Loss    : {APERTURE_INSERTION_LOSS_DB:.2f} dB")
    print(f"Baseline Coverage (>-75dBm): {cov_baseline:.2f}%")
    print(f"Assisted Coverage (>-75dBm): {cov_assisted:.2f}%")
    print("=" * 65)

    # Plotting Results
    plt.figure(figsize=(10, 6))
    plt.contourf(Y, X, rx_power_assisted, levels=50, cmap='viridis')
    cbar = plt.colorbar()
    cbar.set_label('Received Signal Power (dBm)')
    plt.title('Version 2: Single-Axis Canyon Spatial Power Field (28 GHz)')
    plt.xlabel('Street Canyon Distance (Meters)')
    plt.ylabel('Canyon Width (Meters)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('v2_single_axis_coverage.png', dpi=300)
    print("[SUCCESS] Field heatmap saved to 'v2_single_axis_coverage.png'.")

if __name__ == '__main__':
    run_street_canyon_simulation()
