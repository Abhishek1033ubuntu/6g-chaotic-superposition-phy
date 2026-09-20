"""
6G Volumetric Engine - Sub-THz OFDM Dispersion & Doppler Drift Engine
Simulates multi-carrier channel dynamics, Doppler shift (v = 12 m/s elevator motion),
and ICI degradation across sub-THz numerologies (SCS = 120 kHz vs 960 kHz).

Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import matplotlib.pyplot as plt
import numpy as np


class OFDMDopplerEngine:

    def __init__(self, fc=28e9, v_elevator_mps=12.0):
        self.fc = fc
        self.c = 3e8
        self.v_elevator = v_elevator_mps
        self.max_doppler_hz = (self.v_elevator / self.c) * self.fc

    def evaluate_ici_ratio(self, scs_khz_list=[120, 240, 480, 960]):
        """Calculates Inter-Carrier Interference (ICI) power relative to sub-carrier spacing."""
        ici_results = {}
        for scs in scs_khz_list:
            scs_hz = scs * 1e3
            # Normalized Doppler Offset
            eps = self.max_doppler_hz / scs_hz
            # Approximated ICI-to-Signal Power Ratio: P_ICI / P_sig approx (pi^2 / 6) * eps^2
            p_ici_ratio_db = 10 * np.log10((np.pi**2 / 6.0) * (eps**2))
            ici_results[scs] = {
                "max_doppler_hz": round(self.max_doppler_hz, 2),
                "normalized_offset": round(eps, 5),
                "ici_power_db": round(p_ici_ratio_db, 2),
            }
        return ici_results


if __name__ == "__main__":
    engine = OFDMDopplerEngine()
    ici_data = engine.evaluate_ici_ratio()

    print("=================================================================")
    print("--- Sub-THz OFDM Doppler Drift & Numerology Assessment ---")
    print("=================================================================")
    print(f"  Maximum Elevator Doppler Shift (12 m/s): {engine.max_doppler_hz:.2f} Hz")
    for scs, metrics in ici_data.items():
        print(
            f"  SCS = {scs:3d} kHz | Norm Offset: {metrics['normalized_offset']:.5f} | ICI Power: {metrics['ici_power_db']:.2f} dB"
        )

    # Plot ICI Power vs Subcarrier Spacing
    scs_vals = list(ici_data.keys())
    ici_vals = [ici_data[s]["ici_power_db"] for s in scs_vals]

    plt.figure(figsize=(7, 4.5))
    plt.plot(
        scs_vals,
        ici_vals,
        marker="o",
        color="purple",
        linewidth=2,
        markersize=8,
    )
    plt.title("Elevator Shaft Doppler Drift: ICI Power vs Sub-Carrier Spacing")
    plt.xlabel("Sub-Carrier Spacing (kHz)")
    plt.ylabel("Inter-Carrier Interference (dB)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("ofdm_doppler_ici_analysis.png", dpi=300)
    print(
        "\n[SUCCESS] Plot saved to 'v4_unified_phy/ofdm_doppler_ici_analysis.png'."
    )
