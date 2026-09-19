"""
Chaotic Phase-Coded Spreader (ChaCha20 Integration)
Authors: Abhishek Singh & AI Collaborator
"""
import numpy as np
from phy_layer.chacha_phase_cipher import ChaCha20PhaseCipher

class ChaosSpreader:
    def __init__(self, key: bytes = None, nonce: bytes = None):
        # Default fallback 256-bit key and 96-bit nonce for baseline tests
        self.key = key if key else b"6G_CHAOTIC_SUPERPOSITION_KEY_32B"
        self.nonce = nonce if nonce else b"NYC_RF_N12B"
        self.cipher = ChaCha20PhaseCipher(self.key, self.nonce)
        
    def generate_phase_sequence(self, num_subcarriers: int, frame_counter: int = 0) -> np.ndarray:
        return self.cipher.generate_phase_sequence(num_subcarriers, frame_counter)

    def apply_chaos(self, symbols: np.ndarray, chaos_seq: np.ndarray) -> np.ndarray:
        return symbols * chaos_seq

    def remove_chaos(self, rx_symbols: np.ndarray, chaos_seq: np.ndarray) -> np.ndarray:
        return rx_symbols / chaos_seq
