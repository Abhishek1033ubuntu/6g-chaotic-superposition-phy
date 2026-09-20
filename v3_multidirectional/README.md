# 6G Metropolitan Spatial Field & RF Transparency Optimizer

This repository implements a multi-physics simulation engine for 6G sub-THz/mmWave (28 GHz) spatial field propagation in high-rise metropolitan environments. It models building shadow mitigation using phase-coherent forwarding apertures to maintain sub-symbol alignment and eliminate deep street canyon coverage blackouts.

---

## Core Performance Metrics

| Parameter | Unassisted Baseline | Assisted System | Metric Delta / Status |
| :--- | :--- | :--- | :--- |
| **QoS Coverage ($\ge -75\text{ dBm}$)** | 85.52% | **96.17%** | **+10.65% Net Gain** |
| **Mean Grid Power** | -78.40 dBm | **-67.39 dBm** | **+11.01 dB Enhancement** |
| **Spatial Field Variance** | 24.12 dB | **16.76 dB** | **Enhanced Field Uniformity** |
| **Forwarding Insertion Loss ($\Delta_{\text{Tx-Rx}}$)** | N/A | **1.80 dB** | **Target $\le 2.0\text{ dB}$ Met** |
| **Phase Coherence ($\Delta\phi$)** | N/A | **0.05 rad ($1.82^\circ$)** | **$<0.0011\text{ dB}$ Phase Degradation** |

---

## Technical Architecture

1. **Incident-Angle Aware 2D Shadow Forwarding (`multi_dir_optimizer.py`)**:
   - Dynamic AoA calculation from 4 distributed macro gNBs ($NW, NE, SW, SE$).
   - Calculates 2D vector shadow corridors across X/Y axes and applies phase-coherent signal re-radiation ($\Delta \le 1.8\text{ dB}$).

2. **Phase-Coherence Inversion Testing (`phase_inversion_test.py`)**:
   - Benchmarks destructive interference at overlapping wavefront boundaries.
   - Proves phase stability: degradation remains $<0.01\text{ dB}$ at $\Delta\phi = 0.05\text{ rad}$, with link budget collapse occurring only past $160^\circ$ phase error.

---

## Project Directory Structure

```text
├── metropolitan_coverage/
│   ├── multi_dir_optimizer.py    # Main multi-directional 2D spatial simulation engine
│   └── phase_inversion_test.py   # Multi-path phase error and destructive null testing
├── multi_directional_coverage_heatmap.png # Spatial power distribution map
├── phase_inversion_degradation.png       # Phase error vs power degradation curve
├── sim_results.json                      # Exported simulation metrics
└── README.md                             # Architecture & results documentation
```
