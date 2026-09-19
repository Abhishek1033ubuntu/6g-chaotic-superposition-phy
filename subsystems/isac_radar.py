"""
Integrated Sensing and Communications (ISAC) Radar Engine
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import numpy as np


class ISACRadarEngine:
    def __init__(self, num_subcarriers: int = 128, carrier_freq_hz: float = 28e9, subcarrier_spacing_hz: float = 120e3):
        self.K = num_subcarriers
        self.fc = carrier_freq_hz
        self.scs = subcarrier_spacing_hz
        self.c = 3e8

        self.bandwidth = self.K * self.scs
        self.range_resolution = self.c / (2 * self.bandwidth)

    def simulate_radar_backscatter(self, num_frames: int, target_range_m: float, target_velocity_mps: float, snr_db: float = 20.0) -> np.ndarray:
        frame_duration = (self.K + 32) / self.bandwidth
        H_matrix = np.zeros((self.K, num_frames), dtype=complex)

        tau = 2 * target_range_m / self.c
        fd = 2 * target_velocity_mps * self.fc / self.c
        subcarrier_indices = np.arange(self.K)

        for m in range(num_frames):
            t_frame = m * frame_duration
            delay_phase = -2j * np.pi * subcarrier_indices * self.scs * tau
            doppler_phase = 2j * np.pi * fd * t_frame
            H_matrix[:, m] = np.exp(delay_phase + doppler_phase)

        snr_linear = 10 ** (snr_db / 10.0)
        noise_std = 1.0 / np.sqrt(2 * snr_linear)
        noise = (np.random.randn(*H_matrix.shape) + 1j * np.random.randn(*H_matrix.shape)) * noise_std

        return H_matrix + noise

    def process_range_doppler_map_high_res(self, H_matrix: np.ndarray, n_fft_range: int = 1024, n_fft_doppler: int = 512):
        range_profiles = np.fft.ifft(H_matrix, n=n_fft_range, axis=0)
        range_doppler_map = np.fft.fftshift(np.fft.fft(range_profiles, n=n_fft_doppler, axis=1), axes=1)

        rd_power_db = 20 * np.log10(np.abs(range_doppler_map) + 1e-12)
        peak_k, peak_m = np.unravel_index(np.argmax(rd_power_db), rd_power_db.shape)

        oversampled_range_res = self.c / (2 * self.bandwidth * (n_fft_range / self.K))
        estimated_range = peak_k * oversampled_range_res

        frame_duration = (self.K + 32) / self.bandwidth
        doppler_axis_hz = np.fft.fftshift(np.fft.fftfreq(n_fft_doppler, d=frame_duration))
        estimated_fd = doppler_axis_hz[peak_m]
        estimated_velocity_mps = (estimated_fd * self.c) / (2 * self.fc)
        estimated_velocity_kmh = estimated_velocity_mps * 3.6

        return rd_power_db, estimated_range, estimated_velocity_kmh
