# 6G Physical Layer Prototype: Chaotic Phase-Coded OFDM Superposition Architecture

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22856270-blue?style=for-the-badge&logo=zenodo&logoColor=white)](https://doi.org/10.5281/zenodo.22856270) 
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

An end-to-end 6G physical layer architecture integrating **256-bit ARX-20 Physical Layer Security (PLS)** and **Sub-Meter Integrated Sensing and Communications (ISAC)** over millimetric wave (mmWave) OFDM/QAM signals.

---

### Key Technical Features

* **ARX-20 Phase Cipher Engine** (`phy_layer/arx20_phase_cipher.py`): Replaces non-cryptographic chaos generators with a 256-bit symmetric stream cipher state, providing Low Probability of Intercept/Detection (LPI/LPD) with zero cyclic prefix footprint.
* **Sub-Meter ISAC Radar Engine** (`subsystems/isac_radar.py`): Utilizes comb pilot backscatter processing with 1024-point IFFT zero-padding oversampling to achieve **17 cm range precision** and Doppler velocity tracking.
* **C++ SIMD High-Performance Core** (`cpp_core/`): Native vectorized execution in C++ (`-O3 -march=native`) delivering an average frame processing latency of **29.33 microseconds**, satisfying the sub-50 µs real-time hardware buffer threshold for 6G SDR deployments.
* **GNU Radio OOT Module** (`gr-chaotic-phy/`): C++ streaming block implementation ready for deployment on USRP/HackRF platforms.

---

### Performance Benchmarks

| Metric | Target Standard | Achieved Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Communication BER** | $< 10^{-3}$ (Pre-FEC) | **0.000000** | PASS |
| **Radar Range Error** | $< 1.0\text{ m}$ | **0.17 m (17 cm)** | PASS |
| **Velocity Tracking** | Target: $72.0\text{ km/h}$ | **72.32 km/h** | PASS |
| **DSP Frame Latency** | $< 50\text{ µs}$ | **29.33 µs** | PASS |

---

📁 Repository Version History

◆ Version 4: Unified 3D Volumetric & Sub-THz Doppler Engine ( /v4_unified_phy )
• Key Features: 100-floor 3D volumetric matrix solver, dynamic shadowing resilience (+20.55 dB QoS margin), and Sub-THz elevator Doppler drift mitigation.
• Coverage Threshold: 100% Coverage (> -75 dBm) across floor depth and vertical riser levels.
• Sub-Carrier Spacing: 960 kHz SCS suppresses ICI down to -56.50 dB for 12 m/s dynamic motion.

◆ Version 3: Multi-Directional Angle-Aware Steering ( /v3_multidirectional )
• Key Features: Dynamic 2D incident-angle shadow corridors from 4 corner gNBs (NW, NE, SW, SE), Phase-Coherence Inversion & Destructive Null testing ($\Delta\phi = 0.05\text{ rad}$).
• Coverage ($\ge -75\text{ dBm}$): 96.17% (+10.65% Net Gain).
• Mean Power: -67.39 dBm | Spatial Variance: 16.76 dB.

◆ Version 2: Single-Axis Spatial Steering ( /v2_single_axis )
• Key Features: Linear street canyon shadow forwarding, vertical aperture insertion loss modeling ($\le 2.0\text{ dB}$).
• Coverage ($\ge -75\text{ dBm}$): 85.52% baseline vs assisted performance.

◆ Version 1: 1D Baseline Path Loss ( /v1_1d_model )
• Key Features: Basic Free-Space Line of Sight (FSPL) and single-obstacle concrete attenuation modeling.

---

### Directory Structure

```text
6g-chaotic-superposition-phy/
├── channel_models/            # Channel propagation & path loss models
├── cpp_core/                  # C++ SIMD hardware optimization core
│   └── arx20_core.cpp
├── docs/                      # Architectural handoff & deployment docs
├── grc/                       # GNU Radio block YAML configurations
├── hardware_hil/              # Hardware-in-the-loop streaming scripts
├── lib/                       # C++ streaming block implementations
├── mimo_ace/                  # Active Constellation Extension engines
├── paper/                     # Research manuscript & publication drafts
├── phy_layer/                 # Core physical layer pipeline
│   ├── arx20_phase_cipher.py  # 256-Bit cryptographic phase engine
│   ├── chaos_spreader.py      # Physical layer spreading pipeline
│   ├── fde_equalizer.py       # Frequency domain equalization
│   ├── fec_viterbi.py         # Soft-decision Viterbi decoding
│   └── modulation.py          # OFDM/QAM modulation routines
├── subsystems/                # High-level subsystems
│   └── isac_radar.py          # Sub-meter ISAC radar engine
├── v1_1d_model/               # Baseline 1D path loss modeling
├── v2_single_axis/            # Single-axis spatial steering engine
├── v3_multidirectional/       # Multi-directional angle-aware steering
├── v4_unified_phy/            # 3D volumetric matrix solver & Sub-THz Doppler engine
│   ├── vertical_riser_matrix.py
│   ├── ofdm_doppler_sim.py
│   └── README.md
├── gr-chaotic-phy/            # GNU Radio 3.10 Out-Of-Tree (OOT) module
├── CITATION.cff               # Repository citation metadata
├── LICENSE                    # MIT License
├── README.md                  # Master repository documentation
└── sim_runner.py              # End-to-end master verification pipeline

```

---

### Quick Start

#### Run Core Simulation Pipeline

```bash
# Run unified end-to-end simulation
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

### License

Distributed under the MIT License. See `LICENSE` for details.
