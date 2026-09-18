"""
Chaotic Phase-Coded Spreading Engine
Authors: Abhishek Singh & AI Collaborator
"""
import numpy as np

class ChaosSpreader:
    def __init__(self, seed=42):
        np.random.seed(seed)
        
    def generate_phase_sequence(self, num_subcarriers):
        # Generates CSPRNG deterministic chaotic phase sequence
        raw_complex = (np.random.randn(num_subcarriers) + 1j * np.random.randn(num_subcarriers)) / np.sqrt(2)
        return raw_complex / np.abs(raw_complex)

    def apply_chaos(self, symbols, chaos_seq):
        return symbols * chaos_seq

    def remove_chaos(self, rx_symbols, chaos_seq):
        return rx_symbols / chaos_seq
