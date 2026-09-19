"""
6G Physical Layer Security & ISAC Engine
Phase 1: IQ Binary Stream Serialization & CFO/STO Synchronization Core
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import numpy as np
import struct


class IQStreamSync:
    """
    Handles IQ binary serialization/deserialization for SDR hardware
    and performs preamble-assisted STO and CFO estimation/compensation.
    """

    def __init__(self, num_subcarriers=128, cp_length=32, sample_rate_hz=15.36e6):
        self.num_subcarriers = num_subcarriers
        self.cp_length = cp_length
        self.fft_len = num_subcarriers
        self.frame_len = self.fft_len + self.cp_length
        self.sample_rate_hz = sample_rate_hz

    # -------------------------------------------------------------------
    # 1. IQ Binary Serialization (.iq / .bin)
    # -------------------------------------------------------------------
    @staticmethod
    def export_iq_to_bin(iq_samples: np.ndarray, file_path: str):
        """
        Exports complex IQ array to raw binary file (interleaved 32-bit Float I & Q).
        Format: [I0, Q0, I1, Q1, I2, Q2, ...]
        """
        iq_flattened = np.empty(2 * len(iq_samples), dtype=np.float32)
        iq_flattened[0::2] = np.real(iq_samples).astype(np.float32)
        iq_flattened[1::2] = np.imag(iq_samples).astype(np.float32)
        
        with open(file_path, 'wb') as f:
            f.write(iq_flattened.tobytes())
        print(f"[HIL Serializer] Exported {len(iq_samples)} IQ samples -> {file_path}")

    @staticmethod
    def import_iq_from_bin(file_path: str) -> np.ndarray:
        """
        Reads raw binary file (interleaved 32-bit Float) back into complex numpy array.
        """
        with open(file_path, 'rb') as f:
            data = f.read()
        
        raw_floats = np.frombuffer(data, dtype=np.float32)
        i_samples = raw_floats[0::2]
        q_samples = raw_floats[1::2]
        complex_iq = i_samples + 1j * q_samples
        print(f"[HIL Deserializer] Imported {len(complex_iq)} IQ samples <- {file_path}")
        return complex_iq

    # -------------------------------------------------------------------
    # 2. Preamble Generation (Schmidl & Cox Synchronization Sequence)
    # -------------------------------------------------------------------
    def generate_schmidl_cox_preamble(self) -> np.ndarray:
        """
        Generates a 2-part identical time-domain preamble for STO/CFO estimation.
        Half-FFT length PN sequence mapped onto even subcarriers.
        """
        np.random.seed(42)  # Deterministic seed for preamble sync
        pn_seq = 2 * np.random.randint(0, 2, self.num_subcarriers // 2) - 1
        
        freq_preamble = np.zeros(self.num_subcarriers, dtype=complex)
        freq_preamble[0::2] = pn_seq + 1j * pn_seq  # Occupy even subcarriers
        
        time_preamble_half = np.fft.ifft(freq_preamble)
        
        # Preamble structure: [CP | Half 1 | Half 2]
        half_len = self.num_subcarriers // 2
        p1 = time_preamble_half[:half_len]
        time_preamble = np.tile(p1, 2)
        
        # Add Cyclic Prefix
        cp = time_preamble[-self.cp_length:]
        full_preamble = np.concatenate([cp, time_preamble])
        return full_preamble

    # -------------------------------------------------------------------
    # 3. STO & CFO Joint Estimation and Compensation
    # -------------------------------------------------------------------
    def estimate_and_compensate(self, rx_signal: np.ndarray):
        L = self.num_subcarriers // 2
        N_search = len(rx_signal) - 2 * L
        
        P = np.zeros(N_search, dtype=complex)
        R = np.zeros(N_search, dtype=float)
        M = np.zeros(N_search, dtype=float)
        
        for d in range(N_search):
            r1 = rx_signal[d : d + L]
            r2 = rx_signal[d + L : d + 2 * L]
            P[d] = np.sum(np.conj(r1) * r2)
            R[d] = np.sum(np.abs(r2) ** 2)
            if R[d] > 0:
                M[d] = (np.abs(P[d]) ** 2) / (R[d] ** 2)
                
        # 1. Coarse STO Detection
        coarse_sto = np.argmax(M)
        
        # 2. Fractional CFO Estimation & Preliminary Correction
        angle_p = np.angle(P[coarse_sto])
        fractional_cfo_est = angle_p / np.pi
        
        time_indices = np.arange(len(rx_signal))
        cfo_correction_vector = np.exp(-1j * 2 * np.pi * fractional_cfo_est * time_indices / self.num_subcarriers)
        rx_cfo_corr = rx_signal * cfo_correction_vector
        
        # 3. Fine STO Refinement via Cross-Correlation with Known Preamble
        known_preamble = self.generate_schmidl_cox_preamble()[self.cp_length:] # Exclude CP for sharp peak
        xcorr = np.abs(np.correlate(rx_cfo_corr, known_preamble, mode='valid'))
        sto_est = np.argmax(xcorr)
        
        cfo_hz_est = fractional_cfo_est * (self.sample_rate_hz / self.num_subcarriers)
        payload_start = sto_est + len(known_preamble)
        
        return rx_cfo_corr, sto_est, cfo_hz_est, payload_start, M
        
        # 4. Extract Synchronized Frame (Post-Preamble payload start)
        payload_start = sto_est + self.cp_length + self.num_subcarriers
        
        return rx_signal_corrected, sto_est, cfo_hz_est, payload_start, M


if __name__ == "__main__":
    print("=================================================================")
    print("--- Phase 1: HIL IQ Stream & CFO/STO Verification Run ---")
    print("=================================================================\n")

    sync_engine = IQStreamSync(num_subcarriers=128, cp_length=32, sample_rate_hz=15.36e6)

    # 1. Generate Preamble + Random Payload
    preamble = sync_engine.generate_schmidl_cox_preamble()
    payload = (np.random.randn(128 * 4) + 1j * np.random.randn(128 * 4)) / np.sqrt(2)
    tx_stream = np.concatenate([preamble, payload])

    # 2. Export & Import Binary File (.bin)
    file_name = "test_tx_stream.bin"
    sync_engine.export_iq_to_bin(tx_stream, file_name)
    imported_stream = sync_engine.import_iq_from_bin(file_name)

    # 3. Inject Hardware Impairments (STO Delay + CFO Shift + Noise)
    sto_ground_truth = 45  # Sample delay
    cfo_ground_truth_hz = 120e3  # 120 kHz LO offset (~1 subcarrier spacing)
    
    time_axis = np.arange(len(imported_stream))
    normalized_cfo = cfo_ground_truth_hz / (15.36e6 / 128)
    cfo_impairment = np.exp(1j * 2 * np.pi * normalized_cfo * time_axis / 128)
    
    # Apply impairments
    impaired_stream = np.pad(imported_stream * cfo_impairment, (sto_ground_truth, 0), mode='constant')
    
    # Add AWGN
    noise = (np.random.randn(len(impaired_stream)) + 1j * np.random.randn(len(impaired_stream))) * 0.05
    rx_stream = impaired_stream + noise

    # 4. Execute CFO & STO Recovery
    rx_corrected, sto_est, cfo_est_hz, payload_start, metric = sync_engine.estimate_and_compensate(rx_stream)

    sto_error = abs(sto_est - (sto_ground_truth + sync_engine.cp_length))
    cfo_error_hz = abs(cfo_est_hz - cfo_ground_truth_hz)

    print(f"\n[HIL Results]")
    print(f"  Ground Truth: STO Offset = {sto_ground_truth} samples | CFO Offset = {cfo_ground_truth_hz/1e3:.2f} kHz")
    print(f"  Estimated:    STO Index  = {sto_est} samples  | CFO Offset = {cfo_est_hz/1e3:.2f} kHz")
    print(f"  Sync Errors:  STO Error  = {sto_error} samples | CFO Error  = {cfo_error_hz:.2f} Hz")

    if sto_error == 0 and cfo_error_hz < 500.0:
        print("\nHIL VERDICT: SUCCESS — Frame Boundary Synchronized & CFO Corrected (< 500 Hz Residual Error)")
    else:
        print("\nHIL VERDICT: CHECK PARAMETERS")
