"""
Subsystem A: Narrow-Beam Tracking MIMO Array (+18 dB Gain)
Authors: Abhishek Singh & AI Collaborator
"""
import numpy as np

class BeamformerMIMO:
    def __init__(self, gain_db=18.0):
        self.gain_linear = np.sqrt(10**(gain_db / 10))

    def apply_steering(self, tx_signal):
        return tx_signal * self.gain_linear

    def normalize_rx(self, rx_signal):
        return rx_signal / self.gain_linear
