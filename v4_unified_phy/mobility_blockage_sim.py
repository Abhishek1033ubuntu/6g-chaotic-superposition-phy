"""
6G Volumetric Engine - Dynamic Mobility & Transient Human Blockage Simulation
Tests physical-layer resilience under UE motion and dynamic shadow fading
across Floor 50 (0m to 40m depth).

Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import matplotlib.pyplot as plt
import numpy as np


class DynamicBlockageEngine:

    def __init__(self, fc=28e9):
        self.fc = fc
        self.c = 3e8
        self.floor_depth_m = 40.0

        # Base RF Link Parameters
        self.pwr_repeater_base_dbm = 23.5  # Amplified facade base power
        self.tx_gain_db = 12.0  # Radiator antenna gain

        # Human Shadowing Attenuation (Double Knife-Edge Diffraction Model at 28 GHz)
        self.blockage_loss_db = 18.0

    def simulate_ue_walk_path(
        self, steps=200, blockage_start_m=12.0, blockage_end_m=18.0
    ):
        """Simulates a user walking from Window (0m) to Core (40m) with an active

        human blockage zone occurring between blockage_start_m and blockage_end_m.
        """
        user_positions = np.linspace(0.5, 39.5, steps)
        unblocked_power = []
        blocked_power = []

        for pos in user_positions:
            # 1. Front Inward Path
            d_front = np.maximum(pos, 0.5)
            fspl_front = 20 * np.log10(4 * np.pi * d_front * self.fc / self.c)
            p_front = self.pwr_repeater_base_dbm + self.tx_gain_db - fspl_front

            # 2. Rear Outward Path
            d_rear = np.maximum(self.floor_depth_m - pos, 0.5)
            fspl_rear = 20 * np.log10(4 * np.pi * d_rear * self.fc / self.c)
            p_rear = self.pwr_repeater_base_dbm + self.tx_gain_db - fspl_rear

            # Superposition without blockage
            p_tot_mw = 10 ** (p_front / 10.0) + 10 ** (p_rear / 10.0)
            p_tot_dbm = 10 * np.log10(p_tot_mw)
            unblocked_power.append(p_tot_dbm)

            # Apply blockage attenuation if UE enters the shadow zone
            if blockage_start_m <= pos <= blockage_end_m:
                # Assuming blockage affects the dominant line-of-sight path from the front node
                p_front_blocked = p_front - self.blockage_loss_db
                p_tot_blocked_mw = 10 ** (p_front_blocked / 10.0) + 10 ** (
                    p_rear / 10.0
                )
                p_tot_blocked_dbm = 10 * np.log10(p_tot_blocked_mw)
                blocked_power.append(p_tot_blocked_dbm)
            else:
                blocked_power.append(p_tot_dbm)

        return user_positions, unblocked_power, blocked_power


if __name__ == "__main__":
    sim = DynamicBlockageEngine()
    positions, unblocked, blocked = sim.simulate_ue_walk_path()

    print("=================================================================")
    print("--- Dynamic Human Blockage Simulation Summary ---")
    print("=================================================================")
    print(f"  Min Signal (Unblocked) : {np.min(unblocked):.2f} dBm")
    print(
        f"  Min Signal (Blocked Zone 12m-18m) : {np.min(blocked):.2f} dBm"
    )
    print(
        f"  QoS Maintenance Margin : +{np.min(blocked) - (-75.0):.2f} dB"
    )

    # Plot Mobility Profile
    plt.figure(figsize=(8, 5))
    plt.plot(
        positions,
        unblocked,
        color="teal",
        linewidth=2,
        label="Clear LoS Walk Path",
    )
    plt.plot(
        positions,
        blocked,
        color="darkorange",
        linestyle="--",
        linewidth=2,
        label="Path with Human Shadowing (12m - 18m)",
    )
    plt.axhline(
        y=-75.0, color="black", linestyle=":", label="QoS Floor (-75 dBm)"
    )

    plt.axvspan(
        12.0,
        18.0,
        color="orange",
        alpha=0.15,
        label="Active Blockage Region (18 dB Loss)",
    )

    plt.title(
        "Floor 50 UE Mobility: Dynamic Human Blockage vs Dual Mesh Resilience"
    )
    plt.xlabel("Indoor UE Trajectory from Window to Core (Meters)")
    plt.ylabel("Received Power (dBm)")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig("mobility_blockage_coverage.png", dpi=300)
    print(
        "\n[SUCCESS] Plot saved to 'v4_unified_phy/mobility_blockage_coverage.png'."
    )
