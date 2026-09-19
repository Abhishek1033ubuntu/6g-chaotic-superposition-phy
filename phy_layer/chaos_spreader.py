"""
Chaotic Phase-Coded Spreader Engine (ARX-20 PLS Integration)
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import numpy as np
from phy_layer.arx20_phase_cipher import ARX20PhaseCipher


class ChaosSpreader:
    def __init__(self, key: bytes = None, nonce: bytes = None):
        self.key = key if key else b"6G_CHAOTIC_SUPERPOSITION_KEY_32B"
        self.nonce = nonce if nonce else b"NYC_RF_NONCE"
        self.cipher = ARX20PhaseCipher(self.key, self.nonce)

    def generate_phase_sequence(self, num_subcarriers: int, frame_counter: int = 0) -> np.ndarray:
        return self.cipher.generate_phase_sequence(num_subcarriers, frame_counter)

    def apply_chaos(self, symbols: np.ndarray, chaos_seq: np.ndarray) -> np.ndarray:
        return symbols * chaos_seq

    def remove_chaos(self, rx_symbols: np.ndarray, chaos_seq: np.ndarray) -> np.ndarray:
        return rx_symbols / chaos_seq
