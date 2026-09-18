"""
Frequency-Domain MMSE Equalizer with Comb Pilot Tracking
Authors: Abhishek Singh & AI Collaborator
"""
import numpy as np

class FDEMMSEEqualizer:
    def __init__(self, sigma2=1e-3):
        self.sigma2 = sigma2

    def estimate_channel(self, Y_pilots, X_pilots_expected, pilot_indices, N_active):
        H_pilots = Y_pilots / X_pilots_expected
        H_interp = np.interp(np.arange(N_active), pilot_indices, np.real(H_pilots)) + \
                   1j * np.interp(np.arange(N_active), pilot_indices, np.imag(H_pilots))
        return H_interp

    def equalize(self, Y_active, H_interp):
        H_mmse = np.conj(H_interp) / (np.abs(H_interp)**2 + self.sigma2)
        return Y_active * H_mmse
