# 6G Physical Layer Link Budget & Coverage Analysis

**Authors:** Abhishek Singh & AI Collaborator

This document specifies the link budget parameters across Macro, Micro, and Underground Subway Waveguide deployment scenarios.

---

## Link Budget Matrix

| Parameter | Outdoor Macro (Sub-6 GHz) | Micro Street Canyon (NLOS) | Subway Tunnel Waveguide (Subsystem A) |
| :--- | :--- | :--- | :--- |
| **Center Frequency ($f_c$)** | 3.0 GHz | 3.0 GHz | 3.0 GHz |
| **System Bandwidth ($B$)** | 200 MHz Active | 200 MHz Active | 200 MHz Active |
| **Base Station Tx Power ($P_{tx}$)** | 46.0 dBm (40 W) | 30.0 dBm (1 W) | 33.0 dBm (2 W) |
| **Tx Antenna Gain ($G_{tx}$)** | 18.0 dBi (Massive MIMO) | 8.0 dBi | 18.0 dBi (Array Beamformer) |
| **UE Rx Antenna Gain ($G_{rx}$)** | 0.0 dBi | 0.0 dBi | 0.0 dBi |
| **Noise Floor ($N_0$)** | -91.0 dBm | -91.0 dBm | -91.0 dBm |
| **Target Carrier-to-Noise Ratio** | 12.0 dB | 12.0 dB | 14.0 dB |
| **Log-Normal Shadowing Margin** | 8.0 dB | 6.0 dB | 4.0 dB |
| **Body / Penetration Loss** | 15.0 dB (Indoor) | 3.0 dB (Outdoor) | 0.0 dB (In-Car Direct) |
| **Max Allowable Path Loss (MAPL)** | 142.5 dB | 124.0 dB | 136.0 dB |
| **Effective Coverage Radius** | **800 m – 1.2 km** | **150 m – 250 m** | **1.5 km per segment** |
