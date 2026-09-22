# 6G Physical Layer Prototype: Chaotic Phase-Coded OFDM Superposition Architecture

[![Release](https://img.shields.io/badge/Release-v5.0.0--isac-blue?style=for-the-badge&logo=github)](https://github.com/Abhishek1033ubuntu/6g-chaotic-superposition-phy/releases/tag/v5.0.0-isac)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22876354-blue?style=for-the-badge&logo=zenodo&logoColor=white)](https://doi.org/10.5281/zenodo.22876354) 
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22848049-blue?style=for-the-badge&logo=zenodo&logoColor=white)](https://doi.org/10.5281/zenodo.22848049)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0004--6913--096X-A6CE39?style=flat&logo=orcid&logoColor=white)](https://orcid.org/0009-0004-6913-096X) 
[![AI Collaboration](https://img.shields.io/badge/AI--Collaborator-Google%20Gemini-blue?style=flat&logo=google-gemini&logoColor=white)](https://gemini.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![C++20 SIMD](https://img.shields.io/badge/C%2B%2B-20%20SIMD-orange.svg)](https://gcc.gnu.org/)
[![GNU Radio 3.10](https://img.shields.io/badge/GNU%20Radio-3.10%2B-red.svg)](https://www.gnuradio.org/)

**Lead Researcher & Developer:** Abhishek Singh  
**AI Co-Developer & Collaborator:** Google Gemini  
**License:** MIT License  
**Target Classification:** Beyond 5G (B5G) / 6G Physical Layer (3GPP Rel-19/20 Alignment)

An end-to-end 6G physical layer architecture integrating **256-bit ARX-20 Physical Layer Security (PLS)** and **Sub-Meter Integrated Sensing and Communications (ISAC)** over Sub-THz (140 GHz) and mmWave OFDM/QAM signals.

---

### Key Technical Features

* **Sub-THz ISAC Simulation Pipeline** (`v5_isac_phy/run_isac_pipeline.py`): End-to-end $140\text{ GHz}$ physical layer processing chain operating over a shared $2.0\text{ GHz}$ bandwidth, combining multi-target radar tracking and high-throughput communication link evaluation.
* **ARX-20 Phase Cipher Engine** (`phy_layer/arx20_phase_cipher.py`): Replaces non-cryptographic chaos generators with a 256-bit symmetric stream cipher state, providing Low Probability of Intercept/Detection (LPI/LPD) with zero cyclic prefix footprint.
* **Integrated Sensing & Detection Suite** (`subsystems/`): Features 2D CA-CFAR target extraction (`target_detection.py`), Extended Kalman Filtering trajectory tracking (`target_tracking.py`), and radar ambiguity matrix analysis (`ambiguity_matrix.py`).
* **Sub-Meter ISAC Radar Engine** (`subsystems/isac_radar.py`): Utilizes comb pilot backscatter processing with 1024-point IFFT zero-padding oversampling to achieve **17 cm range precision** and Doppler velocity tracking.
* **Physical Layer Security & Eavesdropping Analysis** (`phy_layer/secrecy_capacity_sim.py`, `subsystems/dl_eavesdropper_test.py`): Evaluates secrecy capacity bounds and tests resilience against deep learning-based signal intelligence attacks.
* **C++ SIMD High-Performance Core** (`cpp_core/`): Native vectorized execution in C++ (`-O3 -march=native`) delivering an average frame processing latency of **29.33 microseconds**, satisfying the sub-50 µs real-time hardware buffer threshold for 6G SDR deployments.
* **GNU Radio OOT Module** (`gr-chaotic-phy/`): C++ streaming block implementation ready for deployment on USRP/HackRF platforms.

---

### Performance Benchmarks

| Metric | Target Standard | Achieved Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Communication BER** | $< 10^{-3}$ (Pre-FEC) | **0.000000** | PASS |
| **Sub-THz Operational Frequency** | $100 - 300\text{ GHz}$ | **140 GHz (2.0 GHz BW)** | PASS |
| **Radar Range Precision** | $< 1.0\text{ m}$ | **0.17 m (17 cm)** | PASS |
| **Velocity Tracking** | Target: $72.0\text{ km/h}$ | **72.32 km/h** | PASS |
| **DSP Frame Latency** | $< 50\text{ µs}$ | **29.33 µs** | PASS |

---

### Repository Version History

◆ **Version 5: Integrated Sensing & Communications (ISAC) Module** (`/v5_isac_phy`)
• **Key Features:** $140\text{ GHz}$ Sub-THz master pipeline orchestrator, 2D Range-Doppler FFT processing, 2D CA-CFAR target extraction, Extended Kalman Filter (EKF) tracking, QPSK constellation/BER evaluation, and Pareto-optimal sensing-comm resource allocation ($\alpha$-split).

◆ **Version 4: Unified 3D Volumetric & Sub-THz Doppler Engine** (`/v4_unified_phy`)
• **Key Features:** 100-floor 3D volumetric matrix solver, dynamic shadowing resilience (+20.55 dB QoS margin), and Sub-THz elevator Doppler drift mitigation.
• **Coverage Threshold:** 100% Coverage ($> -75\text{ dBm}$) across floor depth and vertical riser levels.
• **Sub-Carrier Spacing:** $960\text{ kHz}$ SCS suppresses ICI down to $-56.50\text{ dB}$ for $12\text{ m/s}$ dynamic motion.

◆ **Version 3: Multi-Directional Angle-Aware Steering** (`/v3_multidirectional`)
• **Key Features:** Dynamic 2D incident-angle shadow corridors from 4 corner gNBs (NW, NE, SW, SE), Phase-Coherence Inversion & Destructive Null testing ($\Delta\phi = 0.05\text{ rad}$).
• **Coverage ($\ge -75\text{ dBm}$):** 96.17% (+10.65% Net Gain).
• **Mean Power:** $-67.39\text{ dBm}$ | **Spatial Variance:** $16.76\text{ dB}$.

◆ **Version 2: Single-Axis Spatial Steering** (`/v2_single_axis`)
• **Key Features:** Linear street canyon shadow forwarding, vertical aperture insertion loss modeling ($\le 2.0\text{ dB}$).
• **Coverage ($\ge -75\text{ dBm}$):** 85.52% baseline vs assisted performance.

◆ **Version 1: 1D Baseline Path Loss** (`/v1_1d_model`)
• **Key Features:** Basic Free-Space Line of Sight (FSPL) and single-obstacle concrete attenuation modeling.

---

### Directory Structure

```text
6g-chaotic-superposition-phy/
├── channel_models/              # Propagation & spatial path loss models
│   ├── __init__.py
│   ├── ris_nearfield.py         # Reconfigurable Intelligent Surface near-field channel model
│   ├── subway_waveguide.py      # Tunnel & waveguide propagation model
│   └── urban_canyon_nlos.py     # NLOS urban canyon ray-tracing model
├── cpp_core/                    # C++ SIMD hardware optimization core
│   └── arx20_core.cpp
├── docs/                        # Architectural specifications & documentation
│   ├── handoff_architecture.md  # Multi-gNB beam handover & mobility specifications
│   ├── link_budget_analysis.md  # Sub-THz link margin & path loss calculations
│   ├── rf_planning_sitemap.md   # Deployment sitemap & spatial coverage topology
│   └── images/                  # Exported performance plots & diagrams
│       ├── ber_vs_snr.png
│       ├── isac_comm_ber.png
│       ├── isac_target_tracking.png
│       ├── isac_tradeoff_curve.png
│       └── range_doppler_map.png
├── gr-chaotic-phy/              # GNU Radio 3.10 Out-Of-Tree (OOT) module
│   ├── arx20_core.cpp
│   ├── arx20_phase_cipher_cc_impl.cc
│   └── chaotic_phy_arx20_phase_cipher_cc.block.yml
├── grc/                         # GNU Radio block YAML configurations
├── hardware_hil/                # Hardware-in-the-loop streaming scripts
├── lib/                         # C++ streaming block implementations
├── mimo_ace/                    # Active Constellation Extension engines
├── paper/                       # Research manuscript & publication drafts
├── phy_layer/                   # Core physical layer pipeline
│   ├── __init__.py
│   ├── arx20_phase_cipher.py    # 256-Bit cryptographic phase engine
│   ├── chaos_spreader.py        # Physical layer spreading pipeline
│   ├── fde_mmse_equalizer.py    # Frequency domain MMSE equalization
│   ├── secrecy_capacity_sim.py  # Physical layer security & secrecy capacity engine
│   ├── soft_viterbi_fec.py      # Soft-decision Viterbi FEC decoding
│   └── superposition_mux.py     # Multi-user chaotic superposition multiplexing
├── subsystems/                  # Integrated sensing & security subsystems
│   ├── __init__.py
│   ├── ambiguity_matrix.py      # ISAC radar ambiguity function analysis
│   ├── beamformer_mimo.py       # Hybrid analog/digital beamforming engine
│   ├── broad_beam_flood.py      # Broad-beam radar illumination engine
│   ├── comm_performance.py      # PHY BER & constellation evaluation
│   ├── dl_eavesdropper_test.py  # Deep learning eavesdropper resilience test
│   ├── isac_radar.py            # Sub-meter ISAC radar engine
│   ├── isac_tradeoff.py         # Pareto sensing vs. comm allocation
│   ├── target_detection.py      # 2D CA-CFAR object detection engine
│   └── target_tracking.py       # Extended Kalman Filter (EKF) tracking engine
├── v1_1d_model/                 # Baseline 1D path loss modeling
├── v2_single_axis/              # Single-axis spatial steering engine
├── v3_multidirectional/         # Multi-directional angle-aware steering
├── v4_unified_phy/              # 3D volumetric matrix solver & Sub-THz Doppler engine
│   ├── vertical_riser_matrix.py
│   ├── ofdm_doppler_sim.py
│   └── README.md
├── v5_isac_phy/                 # 6G ISAC Advanced PHY Module (140 GHz Sub-THz)
│   ├── run_isac_pipeline.py     # ISAC Master Pipeline Orchestrator
│   └── README.md                # Subsystem architecture & performance dossier
├── CITATION.cff                 # Repository citation metadata
├── LICENSE                      # MIT License
├── README.md                    # Master repository documentation
└── sim_runner.py                # End-to-end master verification pipeline
```
---

### Subsystem Architecture Overview

#### 1. Advanced Physical Layer (`phy_layer/`)

* **ARX-20 Cryptographic Phase Engine (`arx20_phase_cipher.py`):** Dynamic phase rotation for physical layer security.
* **Secrecy Capacity Evaluator (`secrecy_capacity_sim.py`):** Quantifies physical layer secrecy boundaries under passive eavesdropping.
* **Superposition Multiplexing (`superposition_mux.py`) & Equalization (`fde_mmse_equalizer.py`):** Multi-user chaotic spreading with frequency-domain MMSE equalization.

#### 2. ISAC & Security Subsystem Suite (`subsystems/`)

* **Ambiguity Analysis (`ambiguity_matrix.py`):** Evaluates range-Doppler coupled sidelobe behavior under ARX-20 phase encoding.
* **Target Detection & Tracking (`target_detection.py`, `target_tracking.py`):** Implements 2D CA-CFAR target extraction with Extended Kalman Filtering (EKF) for trajectory tracking.
* **Tradeoff & Performance (`comm_performance.py`, `isac_tradeoff.py`):** Calculates system communication BER and constructs Pareto optimization curves between throughput (Gbps) and range resolution (cm).
* **Security & Resilience (`dl_eavesdropper_test.py`):** Evaluates physical layer secrecy against deep-learning-based signal classification attacks.

#### 3. Sub-THz ISAC Master Pipeline (`v5_isac_phy/`)

Contains the orchestrator script (`run_isac_pipeline.py`) executing the full $140\text{ GHz}$ processing flow:

1. **Waveform Synthesis:** ARX-20 Phase-Coded OFDM Signal Generation ($N=1024$ subcarriers, $M=128$ symbols, $B=2.0\text{ GHz}$).
2. **Channel & Target Propagation:** Sub-THz multipath channel transmission and multi-target backscatter signal generation.
3. **Radar Processing:** 2D FFT Range-Doppler Matrix generation, 2D CA-CFAR target extraction, and Extended Kalman Filter (EKF) state estimation.
4. **Communication Evaluation:** Demodulation, soft FEC decoding, BER calculation, and constellation cluster tracking across SNR sweeps.
5. **Pareto Tradeoff Optimization:** Pareto-optimal resource division ($\alpha$-split) balancing communication capacity (Gbps) and radar range resolution (cm).

---

### Quick Start

#### Run Version 5: 140 GHz Sub-THz ISAC Pipeline

```bash
# Execute master end-to-end ISAC pipeline
python v5_isac_phy/run_isac_pipeline.py

```

#### Run Core System & Performance Suites

```bash
# Run unified end-to-end master simulation runner
python sim_runner.py

# Build and execute C++ SIMD Benchmark Core
g++ -O3 -march=native cpp_core/arx20_core.cpp -o arx20_core
./arx20_core

```

#### Run Version 4: 3D Volumetric & Sub-THz Doppler Engines

```bash
# Execute 100-floor volumetric 3D signal coverage solver
python v4_unified_phy/vertical_riser_matrix.py

# Execute Sub-THz OFDM Doppler shift & ICI analysis
python v4_unified_phy/ofdm_doppler_sim.py

```

#### Run Version 3: Multi-Directional Steering Simulation

```bash
# Run latest multi-directional spatial simulation
python v3_multidirectional/metropolitan_coverage/multi_dir_optimizer.py

# Run phase-coherence inversion & interference test
python v3_multidirectional/metropolitan_coverage/phase_inversion_test.py

```

---

### Citation & Research Attribution

If you utilize this physical layer framework, the ARX-20 phase cipher, or the 140 GHz Sub-THz ISAC simulation pipeline in your academic research, software projects, or publications, please cite this repository using the following metadata:

#### BibTeX Citation

```bibtex
@software{singh_2026_6g_chaotic_phy,
  author       = {Singh, Abhishek},
  title        = {6G Physical Layer Prototype: Chaotic Phase-Coded OFDM Superposition Architecture (v5.0.0-isac)},
  month        = sep,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v5.0.0-isac},
  doi          = {10.5281/zenodo.22876354},
  url          = {[https://github.com/Abhishek1033ubuntu/6g-chaotic-superposition-phy](https://github.com/Abhishek1033ubuntu/6g-chaotic-superposition-phy)}
}
```
---

### License

Distributed under the MIT License. See `LICENSE` for details.
