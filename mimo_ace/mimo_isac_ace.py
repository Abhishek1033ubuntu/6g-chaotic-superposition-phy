"""
6G Physical Layer Security & ISAC Engine
Phase 3: 2x2/4x4 MIMO-ISAC DoA Estimation & ACE PAPR Reduction Core
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import numpy as np


class MIMOISACEngine:
    """
    Implements 2x2 / 4x4 MIMO Direction-of-Arrival (DoA) spatial estimation
    and Active Constellation Extension (ACE) PAPR reduction.
    """

    def __init__(self, num_tx=2, num_rx=2, carrier_freq_hz=28e9, ant_spacing_m=0.00535):
        self.num_tx = num_tx
        self.num_rx = num_rx
        self.fc = carrier_freq_hz
        self.wavelength = 3e8 / carrier_freq_hz
        self.d = ant_spacing_m  # Half-wavelength spacing at 28 GHz (~5.35 mm)

    # -------------------------------------------------------------------
    # 1. Active Constellation Extension (ACE) for PAPR Reduction
    # -------------------------------------------------------------------
    def apply_ace_papr_reduction(self, qam_symbols: np.ndarray, target_papr_db: float = 6.0, iterations: int = 5) -> np.ndarray:
        """
        Projects high-peak time-domain OFDM signals into valid constellation-extending
        outer regions, reducing PAPR without introducing in-band distortion or BER degradation.
        """
        time_signal = np.fft.ifft(qam_symbols)
        target_max_abs = np.sqrt(10 ** (target_papr_db / 10.0) * np.mean(np.abs(time_signal) ** 2))

        modified_freq = qam_symbols.copy()

        for _ in range(iterations):
            current_time = np.fft.ifft(modified_freq)
            abs_time = np.abs(current_time)

            peaks_mask = abs_time > target_max_abs
            if not np.any(peaks_mask):
                break

            clipped_time = current_time.copy()
            clipped_time[peaks_mask] = target_max_abs * np.exp(1j * np.angle(current_time[peaks_mask]))

            clipped_freq = np.fft.fft(clipped_time)

            real_diff = np.real(clipped_freq) - np.real(qam_symbols)
            imag_diff = np.imag(clipped_freq) - np.imag(qam_symbols)

            valid_real = np.where(np.sign(np.real(qam_symbols)) == np.sign(real_diff), real_diff, 0)
            valid_imag = np.where(np.sign(np.imag(qam_symbols)) == np.sign(imag_diff), imag_diff, 0)

            modified_freq = qam_symbols + (valid_real + 1j * valid_imag)

        return modified_freq

    @staticmethod
    def calculate_papr_db(signal: np.ndarray) -> float:
        time_domain = np.fft.ifft(signal) if signal.ndim == 1 else signal
        peak_power = np.max(np.abs(time_domain) ** 2)
        avg_power = np.mean(np.abs(time_domain) ** 2)
        return 10 * np.log10(peak_power / avg_power)

    # -------------------------------------------------------------------
    # 2. MIMO MUSIC Direction-of-Arrival (DoA) Estimation
    # -------------------------------------------------------------------
    def estimate_doa_music(self, rx_matrix: np.ndarray, num_targets: int = 1) -> float:
        """
        Calculates spatial covariance matrix R_xx and projects noise subspace
        to estimate target Angle of Arrival (AoA) in degrees using 1D MUSIC.
        """
        N_samples = rx_matrix.shape[1]
        Rxx = (rx_matrix @ rx_matrix.conj().T) / N_samples

        eigenvalues, eigenvectors = np.linalg.eigh(Rxx)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvectors = eigenvectors[:, idx]

        En = eigenvectors[:, num_targets:]

        angles_deg = np.linspace(-90, 90, 361)
        music_spectrum = np.zeros(len(angles_deg))

        for i, theta in enumerate(angles_deg):
            theta_rad = np.radians(theta)
            a = np.exp(-1j * 2 * np.pi * (self.d / self.wavelength) * np.arange(self.num_rx) * np.sin(theta_rad))
            a = a.reshape(-1, 1)

            denom = np.abs(a.conj().T @ En @ En.conj().T @ a)[0, 0]
            music_spectrum[i] = 1.0 / (denom + 1e-12)

        peak_idx = np.argmax(music_spectrum)
        estimated_angle_deg = angles_deg[peak_idx]

        return float(estimated_angle_deg)


if __name__ == "__main__":
    print("=================================================================")
    print("--- Phase 3: MIMO DoA & ACE PAPR Verification Run ---")
    print("=================================================================\n")

    mimo_engine = MIMOISACEngine(num_tx=2, num_rx=4, carrier_freq_hz=28e9)

    np.random.seed(101)
    raw_symbols = (2 * np.random.randint(0, 2, 128) - 1) + 1j * (2 * np.random.randint(0, 2, 128) - 1)
    
    papr_original = mimo_engine.calculate_papr_db(raw_symbols)
    ace_symbols = mimo_engine.apply_ace_papr_reduction(raw_symbols, target_papr_db=4.5, iterations=10)
    papr_reduced = mimo_engine.calculate_papr_db(ace_symbols)

    print(f"[PAPR Engine]")
    print(f"  Original OFDM PAPR : {papr_original:.2f} dB")
    print(f"  ACE Reduced PAPR   : {papr_reduced:.2f} dB")
    print(f"  PAPR Reduction Delta: {papr_original - papr_reduced:.2f} dB\n")

    target_angle_ground_truth = 25.0
    N_snapshots = 200

    theta_rad = np.radians(target_angle_ground_truth)
    steering_vector = np.exp(-1j * 2 * np.pi * (mimo_engine.d / mimo_engine.wavelength) * np.arange(4) * np.sin(theta_rad)).reshape(-1, 1)

    signal_source = (np.random.randn(1, N_snapshots) + 1j * np.random.randn(1, N_snapshots)) / np.sqrt(2)
    noise = 0.1 * (np.random.randn(4, N_snapshots) + 1j * np.random.randn(4, N_snapshots)) / np.sqrt(2)

    rx_array_matrix = steering_vector @ signal_source + noise

    estimated_angle = mimo_engine.estimate_doa_music(rx_array_matrix, num_targets=1)
    doa_error = abs(estimated_angle - target_angle_ground_truth)

    print(f"[MIMO-ISAC DoA Estimation]")
    print(f"  Ground Truth Angle : {target_angle_ground_truth:.1f}°")
    print(f"  MUSIC Estimated    : {estimated_angle:.1f}°")
    print(f"  Estimation Error   : {doa_error:.2f}°\n")

    if papr_reduced < papr_original and doa_error <= 1.0:
        print("PHASE 3 VERDICT: SUCCESS — ACE PAPR Suppressed & 4-Rx DoA Estimated within <= 1.0° Resolution")
    else:
        print("PHASE 3 VERDICT: CHECK PARAMETERS")
