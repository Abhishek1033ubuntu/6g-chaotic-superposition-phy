# Hard vs. Soft Handoff Protocols in High-Mobility Environments

**Authors:** Abhishek Singh & AI Collaborator

---

## 1. Intra-Frequency Soft Handover (CoMP)

For outdoor macro-to-micro transitions and station platform areas:
* **Protocol:** Coordinated Multipoint (CoMP) Dual-Connectivity.
* **Mechanism:** The UE maintains phase sync across adjacent small cells using comb-pilot estimation. Soft-combining subcarrier streams eliminates packet loss during mobile transitions.

---

## 2. Inter-Frequency Hard Handover (Tunnel Entry/Exit)

When transitioning between Outdoor Macro and Underground Waveguide tracks:
* **Trigger Condition:** $A3$ Measurement Report ($RSRP_{\text{target}} - RSRP_{\text{source}} > 3.0\text{ dB}$ sustained over $>40\text{ ms}$).
* **Execution Window:** Break-before-make re-configuration completed in $<15\text{ ms}$.
* **Data Continuity:** The Soft-Decision Viterbi Trellis buffer holds in-flight symbols during link re-establishment, preventing frame drops.
