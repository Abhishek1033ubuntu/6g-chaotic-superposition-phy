"""
Superposition Multiplexing & Subcarrier Muxing Engine
Authors: Abhishek Singh & AI Collaborator
"""
import numpy as np

class SuperpositionMux:
    def __init__(self, alpha=0.48):
        self.alpha = alpha

    def multiplex(self, layer1_bpsk, layer2_qam):
        return layer1_bpsk + self.alpha * layer2_qam

    def demux_sic(self, Y_active, H_est, chaos_seq, layer1_est):
        # Successive Interference Cancellation (SIC)
        L1_reconstructed = layer1_est * chaos_seq
        Y_residual = (Y_active / H_est) - L1_reconstructed
        return Y_residual / (chaos_seq * self.alpha)
