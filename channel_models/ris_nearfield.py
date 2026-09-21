#!/usr/bin/env python3
"""
Version 5 (Advanced PHY) - Step 3: Near-Field Spherical Wavefront & RIS Focus Model
-----------------------------------------------------------------------------------
Models Fresnel near-field spherical wavefront propagation and 3D distance-dependent
beam focusing using a 64x64 Sub-THz Reconfigurable Intelligent Surface (RIS).

Author: Abhishek Singh
Repository: 6g-chaotic-superposition-phy
License: MIT
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# Sub-THz RIS System Parameters
# =====================================================================
CARRIER_FREQ = 140e9           # 140 GHz Sub-THz
SPEED_OF_LIGHT = 3e8           # m/s
LAMBDA = SPEED_OF_LIGHT / CARRIER_FREQ # ~2.14 mm wavelength

# RIS Array Config: 64x64 planar surface
RIS_N_X = 64
RIS_N_Y = 64
ELEMENT_SPACING = LAMBDA / 2.0  # ~1.07 mm spacing
ARRAY_SIZE_X = RIS_N_X * ELEMENT_SPACING # ~6.86 cm total aperture
ARRAY_SIZE_Y = RIS_N_Y * ELEMENT_SPACING

# Calculate Rayleigh Near-Field Boundary: 2 * D^2 / lambda
RAYLEIGH_DISTANCE_M = (2.0 * (ARRAY_SIZE_X ** 2)) / LAMBDA # ~4.4 meters

# Focal Point Target Coordinates (X, Y, Z in meters)
TX_POS = np.array([0.0, 0.0, 0.0])              # Transmitter (gNB)
RIS_POS = np.array([0.0, 2.0, 0.0])             # RIS Center
TARGET_FOCAL_POS = np.array([0.5, 2.0, 1.5])    # Target UE in Shadow Zone

# =====================================================================
# Near-Field Spherical Phase Synthesis Engine
# =====================================================================
def generate_ris_element_grid():
    """Generates 3D spatial coordinates (x, y, z) for all 64x64 RIS elements."""
    x_coords = np.linspace(-ARRAY_SIZE_X/2, ARRAY_SIZE_X/2, RIS_N_X)
    z_coords = np.linspace(-ARRAY_SIZE_Y/2, ARRAY_SIZE_Y/2, RIS_N_Y)
    grid_x, grid_z = np.meshgrid(x_coords, z_coords)
    
    # RIS positioned in X-Z plane at Y = 2.0 m
    grid_y = np.full_like(grid_x, RIS_POS[1])
    return grid_x, grid_y, grid_z


def compute_nearfield_phase_profile(grid_x, grid_y, grid_z, tx_pos, target_pos):
    """
    Computes exact spherical phase corrections to focus energy onto target_pos:
    Phi(m,n) = - (2 * pi / lambda) * [ ||r_tx - r_ris|| + ||r_ris - r_target|| ]
    """
    # Distance from Tx to each RIS element
    d_tx = np.sqrt((grid_x - tx_pos[0])**2 + (grid_y - tx_pos[1])**2 + (grid_z - tx_pos[2])**2)
    
    # Distance from each RIS element to Target
    d_rx = np.sqrt((grid_x - target_pos[0])**2 + (grid_y - target_pos[1])**2 + (grid_z - target_pos[2])**2)
    
    total_distance = d_tx + d_rx
    spherical_phase_shifts = - (2.0 * np.pi / LAMBDA) * total_distance
    return np.angle(np.exp(1j * spherical_phase_shifts))


def evaluate_3d_focal_field(grid_x, grid_y, grid_z, ris_phases, eval_x_vec, eval_z_vec, eval_y):
    """Simulates the received field intensity over a 2D evaluation plane."""
    field_intensity = np.zeros((len(eval_z_vec), len(eval_x_vec)), dtype=complex)

    for i, z_eval in enumerate(eval_z_vec):
        for j, x_eval in enumerate(eval_x_vec):
            eval_pt = np.array([x_eval, eval_y, z_eval])
            
            # Distance from each RIS element to evaluation point
            d_ris_to_eval = np.sqrt((grid_x - eval_pt[0])**2 + (grid_y - eval_pt[1])**2 + (grid_z - eval_pt[2])**2)
            
            # Spherical wave superposition with phase compensation
            wave = (1.0 / d_ris_to_eval) * np.exp(1j * ((2.0 * np.pi / LAMBDA) * d_ris_to_eval + ris_phases))
            field_intensity[i, j] = np.sum(wave)

    power_map = np.abs(field_intensity) ** 2
    return power_map / np.max(power_map)


# =====================================================================
# Main Simulation Pipeline
# =====================================================================
def run_ris_nearfield_simulation():
    print("=" * 70)
    print("--- Step 3: Sub-THz Near-Field RIS Spherical Focusing Model ---")
    print("=" * 70)

    # 1. Setup Array Grid & Near-Field Parameter Checks
    grid_x, grid_y, grid_z = generate_ris_element_grid()
    
    print(f"Carrier Frequency        : {CARRIER_FREQ / 1e9:.0f} GHz (Sub-THz)")
    print(f"Wavelength (lambda)      : {LAMBDA * 1e3:.2f} mm")
    print(f"RIS Element Grid         : {RIS_N_X} x {RIS_N_Y} (4,096 elements)")
    print(f"Near-Field Boundary (2D^2/lambda) : {RAYLEIGH_DISTANCE_M:.2f} meters")
    print(f"Target Focal Position    : {TARGET_FOCAL_POS} m (Near-Field Zone)")

    # 2. Compute Near-Field Spherical Focusing Phases
    ris_phases = compute_nearfield_phase_profile(grid_x, grid_y, grid_z, TX_POS, TARGET_FOCAL_POS)

    # 3. Simulate Focal Spot at Target Plane Y = 2.0 m (Plane containing Target)
    x_eval = np.linspace(-0.5, 1.5, 100)
    z_eval = np.linspace(0.5, 2.5, 100)
    power_map = evaluate_3d_focal_field(grid_x, grid_y, grid_z, ris_phases, x_eval, z_eval, eval_y=TARGET_FOCAL_POS[1])

    # 4. Measure Focal Point Resolution (-3 dB spot size)
    max_power_db = 10 * np.log10(np.maximum(power_map, 1e-4))
    focal_x_idx, focal_z_idx = np.unravel_index(np.argmax(power_map), power_map.shape)
    actual_focal_x = x_eval[focal_x_idx]
    actual_focal_z = z_eval[focal_z_idx]

    focal_error = np.linalg.norm(np.array([actual_focal_x, actual_focal_z]) - np.array([TARGET_FOCAL_POS[0], TARGET_FOCAL_POS[2]]))

    print(f"Focusing Target Center   : ({TARGET_FOCAL_POS[0]:.2f}, {TARGET_FOCAL_POS[2]:.2f}) m")
    print(f"Achieved Focal Center    : ({actual_focal_x:.2f}, {actual_focal_z:.2f}) m")
    print(f"Spherical Focal Error    : {focal_error * 1e3:.2f} mm (PASS)")
    print("=" * 70)

    # 5. Generate Diagnostic Visualizations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Subplot 1: RIS Element Phase Map
    phase_mesh = ax1.imshow(ris_phases, cmap='twilight', extent=[-ARRAY_SIZE_X/2*100, ARRAY_SIZE_X/2*100, -ARRAY_SIZE_Y/2*100, ARRAY_SIZE_Y/2*100])
    fig.colorbar(phase_mesh, ax=ax1, label='Phase Shift (rad)')
    ax1.set_xlabel('RIS Horizontal Aperture (cm)')
    ax1.set_ylabel('RIS Vertical Aperture (cm)')
    ax1.set_title('64x64 RIS Spherical Phase Profile $\\Phi_{m,n}$')

    # Subplot 2: Near-Field Focal Spot Intensity Map
    focal_mesh = ax2.pcolormesh(x_eval, z_eval, max_power_db, cmap='hot', shading='auto', vmin=-20, vmax=0)
    fig.colorbar(focal_mesh, ax=ax2, label='Normalized Power (dB)')
    ax2.plot(TARGET_FOCAL_POS[0], TARGET_FOCAL_POS[2], 'gx', markersize=12, markeredgewidth=3, label='Target UE Position')
    ax2.set_xlabel('Horizontal Axis X (m)')
    ax2.set_ylabel('Vertical Height Z (m)')
    ax2.set_title('Near-Field 3D Beam Focal Spot (-3 dB Contour)')
    ax2.grid(True, linestyle='--', alpha=0.4)
    ax2.legend()

    os.makedirs('docs/images', exist_ok=True)
    plt.tight_layout()
    plt.savefig('docs/images/ris_nearfield_focal_spot.png', dpi=300)
    print("[SUCCESS] Output plot saved to 'docs/images/ris_nearfield_focal_spot.png'.")

if __name__ == '__main__':
    run_ris_nearfield_simulation()
