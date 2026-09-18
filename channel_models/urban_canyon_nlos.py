"""
Urban Canyon Non-Line-of-Sight Channel Model
Authors: Abhishek Singh & AI Collaborator
"""
import numpy as np

class UrbanCanyonNLOS:
    def __init__(self, delays=[0, 4, 12], powers_db=[0, -4.0, -9.0]):
        self.delays = np.array(delays)
        self.powers = 10**(np.array(powers_db) / 10)
        self.powers /= np.sum(self.powers)

    def apply_channel(self, tx_signal, fd, fs):
        t_vec = np.arange(len(tx_signal)) / fs
        rx_signal = np.zeros_like(tx_signal, dtype=complex)
        for idx, delay in enumerate(self.delays):
            h_gain = np.sqrt(self.powers[idx] / 2) * (np.random.randn() + 1j*np.random.randn())
            doppler_phase = np.exp(1j * 2 * np.pi * fd * t_vec)
            delayed = np.roll(tx_signal, delay)
            if delay > 0:
                delayed[:delay] = 0
            rx_signal += h_gain * delayed * doppler_phase
        return rx_signal
