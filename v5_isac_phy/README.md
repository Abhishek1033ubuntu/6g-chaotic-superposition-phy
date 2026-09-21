# 6G ISAC Advanced PHY Simulation Pipeline (140 GHz Sub-THz)

This module implements an end-to-end physical layer processing chain for Integrated Sensing and Communication (ISAC) operating in the Sub-THz band (140 GHz). It demonstrates simultaneous high-throughput communication link evaluation and multi-target radar tracking over a shared $2.0\text{ GHz}$ bandwidth.

---

## Technical Highlights

* **Carrier Frequency:** $140\text{ GHz}$
* **System Bandwidth:** $2.0\text{ GHz}$
* **Waveform Structure:** OFDM with ARX-20 Phase Encoding ($N = 1024$ subcarriers, $M = 128$ symbols per frame)
* **Sensing Subsystem:** 2D FFT Range-Doppler processing, 2D CA-CFAR target detection, and Extended Kalman Filter (EKF) multi-target tracking
* **Communication Subsystem:** QPSK demodulation, Bit Error Rate (BER) evaluation, and constellation cluster tracking across SNR sweeps
* **Resource Allocation:** Pareto optimal tradeoff analysis between communication data rate (Gbps) and radar range resolution (cm)

---

## Simulated Results & Visualizations

### 1. Communication BER & Constellation Degradation

The communication physical layer matches theoretical QPSK BER curves, achieving error-free transmission ($\text{BER} = 0$) at $\text{SNR} \ge 14\text{ dB}$ across $262,144$ evaluated bits. Constellation clusters demonstrate clear state separation as noise decreases from $4\text{ dB}$ to $18\text{ dB}$[cite: 16].

---

### 2. Multi-Target Kalman Tracking

The sensing pipeline tracks three dynamic targets across time, resolving crossing range trajectories (down to $6.80\text{ m}$) and distinguishing positive ($+45\text{ km/h}$) and negative ($-80\text{ km/h}$) Doppler velocity profiles without track swapping[cite: 17].

---

### 3. Sensing vs. Communication Resource Allocation Tradeoff

By varying the bandwidth allocation fraction $\alpha \in [0.1, 0.9]$, the system demonstrates the direct Pareto frontier governing capacity and range resolution[cite: 18]:

* **Maximum Communication Capacity:** $9.05\text{ Gbps}$ at $\alpha = 0.9$[cite: 15, 18]
* **Best Radar Range Resolution:** $8.33\text{ cm}$ at $\alpha = 0.1$[cite: 15, 18]

---

## How to Run

Execute the master pipeline orchestrator to re-run the full simulation suite and export all figures to `docs/images/`:

```bash
python run_isac_pipeline.py

```
