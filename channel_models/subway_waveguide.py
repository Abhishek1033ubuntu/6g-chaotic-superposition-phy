"""
Subway Tunnel Waveguide Multipath Channel Engine
Authors: Abhishek Singh & AI Collaborator
"""
import numpy as np

class SubwayWaveguide:
    def __init__(self, delays=[0, 8, 20], powers_db=[0, -3.0, -6.0], k_factor=6.0):
        self.delays = np.array(delays)
        self.powers = 10**(np.array(powers_db) / 10)
        self.powers /= np.sum(self.powers)
        self.k_factor = k_factor

    def apply_channel(self, tx_signal, fd, fs):
        t_vec = np.arange(len(tx_signal)) / fs
        rx_signal = np.zeros_like(tx_signal, dtype=complex)
        for idx, delay in enumerate(self.delays):
            if idx == 0:
                h_los = np.sqrt(self.k_factor / (self.k_factor + 1))
                h_scatter = np.sqrt(1 / (self.k_factor + 1)) * (np.random.randn() + 1j*np.random.randn()) / np.sqrt(2)
                h_gain = np.sqrt(self.powers[idx]) * (h_los + h_scatter)
            else:
                h_gain = np.sqrt(self.powers[idx] / 2) * (np.random.randn() + 1j*np.random.randn())
            
            doppler = np.exp(1j * 2 * np.pi * fd * t_vec)
            delayed = np.roll(tx_signal, delay)
            if delay > 0:
                delayed[:delay] = 0
            rx_signal += h_gain * delayed * doppler
        return rx_signal
