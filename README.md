# 6G Physical Layer Prototype: Chaotic Phase-Coded OFDM Superposition Architecture

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.22842874-blue?style=for-the-badge&logo=zenodo&logoColor=white)](https://doi.org/10.5281/zenodo.22842874) 
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

---
An end-to-end 6G physical layer architecture integrating **256-bit ARX-20 Physical Layer Security (PLS)** and **Sub-Meter Integrated Sensing and Communications (ISAC)** over millimetric wave (mmWave) OFDM/QAM signals.

---

## Key Technical Features

* **ARX-20 Phase Cipher Engine (`phy_layer/arx20_phase_cipher.py`)**: Replaces non-cryptographic chaos generators with a 256-bit symmetric stream cipher state, providing Low Probability of Intercept/Detection (LPI/LPD) with zero cyclic prefix footprint.
* **Sub-Meter ISAC Radar Engine (`subsystems/isac_radar.py`)**: Utilizes comb pilot backscatter processing with 1024-point IFFT zero-padding oversampling to achieve **17 cm range precision** and Doppler velocity tracking.
* **C++ SIMD High-Performance Core (`cpp_core/`)**: Native vectorized execution in C++ (`-O3 -march=native`) delivering an average frame processing latency of **29.33 microseconds**, satisfying the sub-50 µs real-time hardware buffer threshold for 6G SDR deployments.
* **GNU Radio OOT Module (`gr-chaotic-phy/`)**: C++ streaming block implementation ready for deployment on USRP/HackRF platforms.

---

## Performance Benchmarks

| Metric | Target Standard | Achieved Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Communication BER** | $< 10^{-3}$ (Pre-FEC) | **0.000000** | PASS |
| **Radar Range Error** | $< 1.0\text{ m}$ | **0.17 m (17 cm)** | PASS |
| **Velocity Tracking** | Target: $72.0\text{ km/h}$ | **72.32 km/h** | PASS |
| **DSP Frame Latency** | $< 50\ \mu\text{s}$ | **29.33 }\mu\text{s}** | PASS |

---

## Directory Structure

```text
6g-chaotic-superposition-phy/
├── cpp_core/
│   └── arx20_core.cpp             # C++ SIMD Hardware Optimization Core
├── phy_layer/
│   ├── arx20_phase_cipher.py      # 256-Bit Cryptographic Phase Engine
│   ├── chaos_spreader.py          # Physical Layer Spreading Pipeline
│   ├── modulation.py
│   ├── fec_viterbi.py
│   └── fde_equalizer.py
├── subsystems/
│   └── isac_radar.py              # Sub-Meter ISAC Radar Engine
├── gr-chaotic-phy/                # GNU Radio 3.10 Out-Of-Tree Module
├── sim_runner.py                  # End-to-End Master Verification Pipeline
├── README.md
└── LICENSE
```
Quick Start
```
Python Simulation Pipeline
Bash
# Run unified end-to-end simulation
python sim_runner.py
Build C++ SIMD Benchmark Core
Bash
g++ -O3 -march=native cpp_core/arx20_core.cpp -o arx20_core
./arx20_core
```
# License
Distributed under the MIT License. See LICENSE for details.


---

### Local Git Commands to Update Repository

```bash
git add 6g-chaotic-superposition-phy/ README.md
git commit -m "v1.2.0: Add GNU Radio OOT C++ architecture and updated project documentation"
git push origin main
```
