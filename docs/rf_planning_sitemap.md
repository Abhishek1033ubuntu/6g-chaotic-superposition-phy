```markdown
# Comprehensive Metropolitan RF Planning & Site Architecture

**Authors:** Abhishek Singh & AI Collaborator

This document details the network deployment parameters, frequency allocations, hardware site plans, and backhaul topology for a tier-1 metropolitan deployment (New York City Model).

---

## 1. Spectrum Allocation & Duplexing

* **Duplexing Scheme:** Frequency Division Duplexing (FDD)
* **Downlink (DL) Band:** 3400 MHz – 3500 MHz (100 MHz Bandwidth)
* **Guard Band:** 3500 MHz – 3520 MHz (20 MHz Blank Path for cross-duplex isolation)
* **Uplink (UL) Band:** 3520 MHz – 3620 MHz (100 MHz Bandwidth)
* **Frequency Reuse:** $K=1$ with Fractional Frequency Reuse (FFR) to eliminate cell-edge interference.

---

## 2. Infrastructure & Tower Categorization

### Macro Towers (Roof-top / Monopole)
* **Coverage Radius:** $800\text{ m} - 1.2\text{ km}$
* **Tx Power:** 46 dBm (40 W)
* **Antenna Configuration:** $16 \times 16$ Massive MIMO Active Antenna Units (AAU)
* **Active Subscribers:** Up to 3,600 connected UEs per 3-sector site

### Micro / Small Cells (Street Lamp Posts / Facades)
* **Coverage Radius:** $150\text{ m} - 250\text{ m}$
* **Tx Power:** 30 dBm (1 W)
* **Antenna Configuration:** $4 \times 4$ SU-MIMO / MU-MIMO
* **Active Subscribers:** Up to 300 connected UEs per node

### Subway Waveguide Nodes (Subsystem A + B)
* **Coverage Radius:** $1.5\text{ km}$ per track segment
* **Tx Power:** 33 dBm
* **Antenna Configuration:** Directional Phased Arrays + Overhead Leaky Feeder Coax
* **Active Subscribers:** Up to 1,200 connected UEs per station/track sector

---

## 3. Backhaul Architecture

* **Primary Backhaul (80% Sites):** 25 Gbps Dark Fiber eCPRI rings.
* **Secondary Backhaul (20% Sites):** E-Band Millimeter-Wave Microwave links (71–76 GHz / 81–86 GHz) supplying up to 10 Gbps line-of-sight backhaul with adaptive modulation (QPSK to 256-QAM).

---

## 4. Subscriber Throughput Metrics

* **Dedicated Voice Allocation:** 64 kbps low-latency VoNR equivalent channel.
* **Nominal Data Throughput:** 25 Mbps per subscriber.
* **Peak Burst Data Rate:** Up to 250 Mbps per subscriber.
