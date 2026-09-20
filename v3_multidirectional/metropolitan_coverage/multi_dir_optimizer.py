"""
6G Metropolitan Spatial Field & Transparency Optimizer (Multi-Directional Steering)
Calculates dynamic 2D shadow vectors (X/Y axes) based on dominant AoA from Macro gNBs.
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import json
import matplotlib.pyplot as plt
import numpy as np


class MultiDirectionalSpatialOptimizer:

    def __init__(self, grid_size_m=1000, grid_resolution_m=10):
        self.grid_size = grid_size_m
        self.res = grid_resolution_m
        self.num_bins = grid_size_m // grid_resolution_m
        self.fc = 28e9

        # Macro gNB Base Station Locations (Corners of 1km grid)
        self.gnbs = [
            {"id": "NW", "x": 50, "y": 950},
            {"id": "NE", "x": 950, "y": 950},
            {"id": "SW", "x": 50, "y": 50},
            {"id": "SE", "x": 950, "y": 50},
        ]

        # High-Rise Buildings: (x, y, width, depth, height)
        self.buildings = [
            {"id": 1, "x": 200, "y": 200, "w": 60, "d": 60, "h": 150},
            {"id": 2, "x": 200, "y": 500, "w": 80, "d": 80, "h": 220},
            {"id": 3, "x": 200, "y": 800, "w": 50, "d": 50, "h": 90},
            {"id": 4, "x": 500, "y": 300, "w": 100, "d": 70, "h": 350},
            {"id": 5, "x": 500, "y": 700, "w": 70, "d": 70, "h": 180},
            {"id": 6, "x": 800, "y": 200, "w": 60, "d": 60, "h": 110},
            {"id": 7, "x": 800, "y": 500, "w": 90, "d": 60, "h": 260},
            {"id": 8, "x": 800, "y": 800, "w": 70, "d": 70, "h": 140},
        ]

    def _path_loss(self, dist_m):
        dist_m = np.maximum(dist_m, 1.0)
        return 20 * np.log10(dist_m) + 20 * np.log10(self.fc) - 147.55

    def run_multi_directional_simulation(self, tx_power_dbm=46.0):
        grid_x = np.linspace(0, self.grid_size, self.num_bins)
        grid_y = np.linspace(0, self.grid_size, self.num_bins)
        X, Y = np.meshgrid(grid_x, grid_y)

        # Base Free-Space Line of Sight Field Synthesis
        base_power_map = np.full((self.num_bins, self.num_bins), -120.0)
        for gnb in self.gnbs:
            dist = np.sqrt((X - gnb["x"]) ** 2 + (Y - gnb["y"]) ** 2)
            pl = self._path_loss(dist)
            rx_pwr = tx_power_dbm - pl
            base_power_map = np.maximum(base_power_map, rx_pwr)

        unassisted_map = base_power_map.copy()
        assisted_map = base_power_map.copy()

        # Dynamic 2D Angle-Aware Shadow & Forwarding Calculation
        for b in self.buildings:
            x_min, x_max = (b["x"] - b["w"] // 2) // self.res, (
                b["x"] + b["w"] // 2
            ) // self.res
            y_min, y_max = (b["y"] - b["d"] // 2) // self.res, (
                b["y"] + b["d"] // 2
            ) // self.res

            x_min, x_max = max(0, x_min), min(self.num_bins, x_max)
            y_min, y_max = max(0, y_min), min(self.num_bins, y_max)

            # Core Attenuation (> 80 dB Concrete/Steel Shielding)
            unassisted_map[y_min:y_max, x_min:x_max] -= 80.0
            assisted_map[y_min:y_max, x_min:x_max] -= 80.0

            # Calculate dominant Incident Rays from nearest gNB to building center
            gnb_distances = [
                np.sqrt((gnb["x"] - b["x"]) ** 2 + (gnb["y"] - b["y"]) ** 2)
                for gnb in self.gnbs
            ]
            nearest_gnb = self.gnbs[np.argmin(gnb_distances)]

            # Incident Vector (dx, dy)
            dx = b["x"] - nearest_gnb["x"]
            dy = b["y"] - nearest_gnb["y"]
            norm = np.sqrt(dx**2 + dy**2)
            dir_x, dir_y = dx / norm, dy / norm

            # Project 2D Shadow Corridor along incident direction vector
            shadow_length_m = 150.0
            steps = int(shadow_length_m // self.res)

            for step in range(1, steps + 1):
                offset_x = int(round(dir_x * step))
                offset_y = int(round(dir_y * step))

                sh_xmin = max(0, min(self.num_bins, x_min + offset_x))
                sh_xmax = max(0, min(self.num_bins, x_max + offset_x))
                sh_ymin = max(0, min(self.num_bins, y_min + offset_y))
                sh_ymax = max(0, min(self.num_bins, y_max + offset_y))

                # Unassisted System: Deep 2D Multi-Directional Shadow (-35 dB drop)
                unassisted_map[sh_ymin:sh_ymax, sh_xmin:sh_xmax] = np.minimum(
                    unassisted_map[sh_ymin:sh_ymax, sh_xmin:sh_xmax],
                    base_power_map[sh_ymin:sh_ymax, sh_xmin:sh_xmax] - 35.0,
                )

                # Assisted System: RF Invisibility Forwarding (Delta = 1.8 dB)
                assisted_map[sh_ymin:sh_ymax, sh_xmin:sh_xmax] = np.minimum(
                    assisted_map[sh_ymin:sh_ymax, sh_xmin:sh_xmax],
                    base_power_map[sh_ymin:sh_ymax, sh_xmin:sh_xmax] - 1.8,
                )

        # Compute Quality & Transparency Metrics
        target_qos_dbm = -75.0
        unassisted_cov = np.mean(unassisted_map >= target_qos_dbm) * 100.0
        assisted_cov = np.mean(assisted_map >= target_qos_dbm) * 100.0

        return {
            "unassisted_qos_coverage_pct": round(float(unassisted_cov), 2),
            "assisted_qos_coverage_pct": round(float(assisted_cov), 2),
            "field_coverage_gain_pct": round(
                float(assisted_cov - unassisted_cov), 2
            ),
            "field_uniformity_std_dev_db": round(
                float(np.std(assisted_map)), 2
            ),
            "min_grid_power_dbm": round(float(np.min(assisted_map)), 2),
            "mean_grid_power_dbm": round(float(np.mean(assisted_map)), 2),
            "assisted_map": assisted_map,
        }


if __name__ == "__main__":
    opt = MultiDirectionalSpatialOptimizer()
    results = opt.run_multi_directional_simulation(tx_power_dbm=46.0)
    assisted_map = results.pop("assisted_map")

    print("=================================================================")
    print("--- 6G Multi-Directional Incident-Angle Aware Optimization ---")
    print("=================================================================\n")

    print(f"[Field Transparency Metrics (Target QoS >= -75 dBm)]")
    print(
        f"  Unassisted System Coverage : {results['unassisted_qos_coverage_pct']}%"
    )
    print(
        f"  RF Invisible System Coverage: {results['assisted_qos_coverage_pct']}%"
    )
    print(
        f"  Field Quality Gain Delta   : +{results['field_coverage_gain_pct']}%\n"
    )

    print(f"[Signal Fidelity & Uniformity]")
    print(f"  Mean Grid Power Level     : {results['mean_grid_power_dbm']} dBm")
    print(
        f"  Spatial Field Variance    : {results['field_uniformity_std_dev_db']} dB\n"
    )

    # Export metrics to JSON
    with open("sim_results.json", "w") as f:
        json.dump(results, f, indent=4)

    plt.figure(figsize=(9, 7))
    plt.imshow(
        assisted_map,
        extent=[0, 1000, 0, 1000],
        origin="lower",
        cmap="viridis",
        vmin=-100,
        vmax=-40,
    )
    plt.colorbar(label="Received Power (dBm)")
    plt.title(
        "6G Metropolitan Coverage: Multi-Directional Angle-Aware Forwarding"
    )
    plt.xlabel("Grid X (meters)")
    plt.ylabel("Grid Y (meters)")
    plt.tight_layout()
    plt.savefig("multi_directional_coverage_heatmap.png", dpi=300)
    print(
        "[OUTPUT GENERATED] Saved heatmap to 'multi_directional_coverage_heatmap.png' and metrics to 'sim_results.json'."
    )
