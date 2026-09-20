"""
6G Phase-Coherence Inversion & Overlap Interference Tester
Evaluates QoS impact and destructive null creation under phase error degradation.
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import matplotlib.pyplot as plt
import numpy as np


class PhaseInversionTester:

    def __init__(self, fc=28e9):
        self.fc = fc
        self.wavelength = 3e8 / fc  # ~10.7 mm wave

    def simulate_phase_degradation(
        self, base_power_dbm=-65.0, phase_errors_rad=None
    ):
        if phase_errors_rad is None:
            phase_errors_rad = np.linspace(0, np.pi, 100)

        results = []

        # Reference wave 1 (Primary Forwarder)
        E1 = np.sqrt(10 ** (base_power_dbm / 10.0))

        for delta_phi in phase_errors_rad:
            # Overlapping wave 2 with phase offset delta_phi
            # E_total = E1 + E1 * exp(j * delta_phi)
            E_total = E1 * (1 + np.cos(delta_phi) + 1j * np.sin(delta_phi))
            pwr_total_mw = np.abs(E_total) ** 2
            pwr_total_dbm = (
                10 * np.log10(pwr_total_mw) if pwr_total_mw > 1e-15 else -160.0
            )

            # Destructive Null Depth relative to constructive peak (+6.02 dB)
            null_depth_db = pwr_total_dbm - (base_power_dbm + 6.020599)

            results.append(
                {
                    "phase_error_rad": float(delta_phi),
                    "phase_error_deg": float(np.degrees(delta_phi)),
                    "combined_power_dbm": float(pwr_total_dbm),
                    "relative_null_depth_db": float(null_depth_db),
                }
            )

        return phase_errors_rad, results


if __name__ == "__main__":
    tester = PhaseInversionTester()
    phase_range, test_results = tester.simulate_phase_degradation()

    # Benchmark points
    phase_0_05 = [r for r in test_results if r["phase_error_rad"] <= 0.05][-1]
    phase_pi_4 = [
        r for r in test_results if r["phase_error_deg"] <= 45.0 * (180 / 180)
    ][-1]
    phase_pi = test_results[-1]

    print("=================================================================")
    print("--- 6G Phase-Coherence Inversion & Destructive Null Test ---")
    print("=================================================================\n")

    print("[Phase Alignment Benchmarks]")
    print(
        f"  Target Threshold (0.05 rad / {phase_0_05['phase_error_deg']:.2f}°):"
    )
    print(
        f"    Combined Signal Power : {phase_0_05['combined_power_dbm']:.2f} dBm"
    )
    print(
        f"    Signal Degradation    : {phase_0_05['relative_null_depth_db']:.4f} dB\n"
    )

    print(
        f"  Moderate Phase Drift (pi/4 / {phase_pi_4['phase_error_deg']:.2f}°):"
    )
    print(
        f"    Combined Signal Power : {phase_pi_4['combined_power_dbm']:.2f} dBm"
    )
    print(
        f"    Signal Degradation    : {phase_pi_4['relative_null_depth_db']:.2f} dB\n"
    )

    print(
        f"  Complete Anti-Phase Inversion (pi / {phase_pi['phase_error_deg']:.2f}°):"
    )
    print(
        f"    Combined Signal Power : {phase_pi['combined_power_dbm']:.2f} dBm"
    )
    print(
        f"    Deep Null Attenuation : {phase_pi['relative_null_depth_db']:.2f} dB\n"
    )

    plt.figure(figsize=(8, 5))
    degs = [r["phase_error_deg"] for r in test_results]
    pwrs = [r["combined_power_dbm"] for r in test_results]

    plt.plot(
        degs,
        pwrs,
        color="crimson",
        linewidth=2,
        label="Overlapping Multi-Path Power",
    )
    plt.axvline(
        x=2.86,
        color="green",
        linestyle="--",
        label="Target Delta-Phi (0.05 rad)",
    )
    plt.axhline(
        y=-75.0, color="black", linestyle=":", label="QoS Threshold (-75 dBm)"
    )

    plt.title("6G Phase Error vs. Multi-Path Destructive Interference")
    plt.xlabel("Phase Error Delta-Phi (Degrees)")
    plt.ylabel("Combined Power (dBm)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("phase_inversion_degradation.png", dpi=300)
    print(
        "[OUTPUT GENERATED] Saved degradation plot to 'phase_inversion_degradation.png'."
    )
