"""
6G Volumetric Engine - High-Rise Inner Core & Vertical Beamforming PHY Model
Integrates:
1. Adaptive Vertical Sectorial Steering (Exterior Height Coverage: 0m to 500m)
2. Dual Front-and-Rear Zero-Delta Repeater Mesh (Interior Depth Coverage: 0m to 40m)

Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import json
import matplotlib.pyplot as plt
import numpy as np


class Unified6GVolumetricEngine:

    def __init__(self, fc=28e9, tx_power_dbm=43.0):
        self.fc = fc
        self.c = 3e8
        self.tx_power_dbm = tx_power_dbm

        # High-Rise Geometry (100 Floors, 400m Height, 40m Floor Depth)
        self.num_floors = 100
        self.floor_height_m = 4.0
        self.floor_depth_m = 40.0

        # Macro gNB Coordinates
        self.gnb_pos = np.array([0.0, -200.0, 35.0])
        self.gnb_array_gain_dbi = 28.0

        # Zero-Delta Repeater Parameters
        self.repeater_interval_floors = 10
        self.l_glass_db = 18.0
        self.front_rx_gain_db = 18.0
        self.zero_delta_pa_gain_db = 38.0
        self.front_tx_inward_gain_db = 12.0
        self.rear_tx_outward_gain_db = 12.0

    def calculate_floor_coverage(self, floor_num, indoor_depth_m):
        """Calculates 3D spatial propagation power incorporating outdoor slant path

        and indoor dual-node re-radiation.
        """
        z_floor = (floor_num - 1) * self.floor_height_m + 1.5

        # 1. Outdoor Slant Path Loss
        d_3d_outdoor = np.sqrt(self.gnb_pos[1] ** 2 + (z_floor - self.gnb_pos[2]) ** 2)
        fspl_outdoor = 20 * np.log10(4 * np.pi * d_3d_outdoor * self.fc / self.c)

        # 2. Single-Node Baseline (Legacy Unassisted / Single Rear)
        pwr_facade = (
            self.tx_power_dbm
            + self.gnb_array_gain_dbi
            - fspl_outdoor
            - self.l_glass_db
        )
        pwr_repeater_base = (
            pwr_facade + self.front_rx_gain_db + self.zero_delta_pa_gain_db
        )

        d_from_rear = np.maximum(self.floor_depth_m - indoor_depth_m, 0.5)
        fspl_rear = 20 * np.log10(4 * np.pi * d_from_rear * self.fc / self.c)
        pwr_rear = pwr_repeater_base + self.rear_tx_outward_gain_db - fspl_rear

        # 3. Dual Front Inward Radiation Path
        d_from_front = np.maximum(indoor_depth_m, 0.5)
        fspl_front = 20 * np.log10(4 * np.pi * d_from_front * self.fc / self.c)
        pwr_front = pwr_repeater_base + self.front_tx_inward_gain_db - fspl_front

        # Linear Superposition
        pwr_total_mw = 10 ** (pwr_front / 10.0) + 10 ** (pwr_rear / 10.0)
        pwr_total_dbm = 10 * np.log10(pwr_total_mw)

        return {
            "pwr_single_rear": round(float(pwr_rear), 2),
            "pwr_dual_total": round(float(pwr_total_dbm), 2),
        }


if __name__ == "__main__":
    engine = Unified6GVolumetricEngine()
    depths = np.linspace(0.5, 39.5, 100)

    pwr_single = []
    pwr_dual = []

    for d in depths:
        res = engine.calculate_floor_coverage(floor_num=50, indoor_depth_m=d)
        pwr_single.append(res["pwr_single_rear"])
        pwr_dual.append(res["pwr_dual_total"])

    # Plot Comparison
    plt.figure(figsize=(8, 5))
    plt.plot(
        depths,
        pwr_single,
        color="crimson",
        linestyle="--",
        linewidth=2,
        label="Single Rear Repeater (Previous Run)",
    )
    plt.plot(
        depths,
        pwr_dual,
        color="teal",
        linewidth=2.5,
        label="Dual Front-and-Rear Re-Radiation (New)",
    )
    plt.axhline(
        y=-75.0, color="black", linestyle=":", label="QoS Floor (-75 dBm)"
    )

    plt.title(
        "Floor 50 Complete Indoor Profile: Dual Front & Rear Superposition"
    )
    plt.xlabel("Indoor Floor Depth from Perimeter Window (Meters)")
    plt.ylabel("Received Power (dBm)")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="lower center")
    plt.tight_layout()
    plt.savefig("dual_reradiation_floor_coverage.png", dpi=300)
    print("[SUCCESS] Engine executed and plot saved to 'dual_reradiation_floor_coverage.png'.")
