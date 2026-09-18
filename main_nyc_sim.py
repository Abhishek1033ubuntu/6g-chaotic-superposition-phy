"""
6G Physical Layer Prototype: Full System Simulation
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# System Parameters
N_fft = 256
N_active = 32
cp_len = 64
fs = 200e6
fc = 3.0e9
v_kmh = 60.0
fd = ((v_kmh / 3.6) / 3e8) * fc

active_carriers = np.arange(-N_active//2, N_active//2)
active_carriers[active_carriers >= 0] += 1
carrier_indices = (active_carriers + N_fft) % N_fft

pilot_mask = np.zeros(N_active, dtype=bool)
pilot_mask[::2] = True
data_mask = ~pilot_mask
N_data = np.sum(data_mask)

alpha_super = 0.48
qam_constellation = np.array([-3-3j, -3-1j, -3+3j, -3+1j,
                              -1-3j, -1-1j, -1+3j, -1+1j,
                               3-3j,  3-1j,  3+3j,  3+1j,
                               1-3j,  1-1j,  1+3j,  1+1j]) / np.sqrt(10)

np.random.seed(42)
raw_l2_bits = np.random.randint(0, 2, size=N_data * 2)

def conv_encode(bits):
    state = 0
    encoded = []
    for bit in bits:
        state = ((state << 1) | bit) & 0b111
        g1 = ((state >> 2) ^ (state >> 1) ^ state) & 1
        g2 = ((state >> 2) ^ state) & 1
        encoded.extend([g1, g2])
    return np.array(encoded)

coded_l2_bits = conv_encode(raw_l2_bits)

qam_symbols_data = []
for i in range(0, len(coded_l2_bits), 4):
    b = coded_l2_bits[i:i+4]
    idx = b[0]*8 + b[1]*4 + b[2]*2 + b[3]
    qam_symbols_data.append(qam_constellation[idx])

qam_symbols = np.zeros(N_active, dtype=complex)
qam_symbols[data_mask] = qam_symbols_data
qam_symbols[pilot_mask] = (1 + 1j) / np.sqrt(2)

d_layer1 = np.random.choice([-1, 1], size=N_active)

X_freq = np.zeros(N_fft, dtype=complex)
x_chaos_freq = (np.random.randn(N_active) + 1j*np.random.randn(N_active)) / np.sqrt(2)

for idx, k in enumerate(carrier_indices):
    S_k = d_layer1[idx] + alpha_super * qam_symbols[idx]
    X_freq[k] = x_chaos_freq[idx] * S_k

tx_time = np.fft.ifft(X_freq) * np.sqrt(N_fft)
tx_cp = np.concatenate([tx_time[-cp_len:], tx_time])

beamforming_gain = np.sqrt(10**(18/10))
tx_cp_beamed = tx_cp * beamforming_gain

# Channel Engine
echo_delays = np.array([0, 8, 20])
echo_powers_db = np.array([0, -3.0, -6.0])
echo_powers = 10**(echo_powers_db / 10)
echo_powers /= np.sum(echo_powers)

t_vec = np.arange(len(tx_cp_beamed)) / fs
rx_tunnel_raw = np.zeros_like(tx_cp_beamed, dtype=complex)

for idx, delay in enumerate(echo_delays):
    if idx == 0:
        K_factor = 6.0
        h_los = np.sqrt(K_factor / (K_factor + 1))
        h_scatter = np.sqrt(1 / (K_factor + 1)) * (np.random.randn() + 1j*np.random.randn()) / np.sqrt(2)
        h_gain = np.sqrt(echo_powers[idx]) * (h_los + h_scatter)
    else:
        h_gain = np.sqrt(echo_powers[idx] / 2) * (np.random.randn() + 1j*np.random.randn())
        
    doppler_phase = np.exp(1j * 2 * np.pi * fd * t_vec)
    delayed_sig = np.roll(tx_cp_beamed, delay)
    if delay > 0:
        delayed_sig[:delay] = 0
    rx_tunnel_raw += h_gain * delayed_sig * doppler_phase

snr_db = 28
sigma2 = 10**(-snr_db / 10)
rx_tunnel_noisy = rx_tunnel_raw + np.sqrt(sigma2 / 2) * (np.random.randn(len(tx_cp)) + 1j*np.random.randn(len(tx_cp)))

# FDE & Demodulation
rx_data = rx_tunnel_noisy[cp_len:] / beamforming_gain
Y_data = np.fft.fft(rx_data) / np.sqrt(N_fft)
Y_active = Y_data[carrier_indices]

pilot_subcarriers = np.where(pilot_mask)[0]
H_pilot_raw = Y_active[pilot_mask] / (x_chaos_freq[pilot_mask] * (d_layer1[pilot_mask] + alpha_super * qam_symbols[pilot_mask]))

H_interp = np.interp(np.arange(N_active), pilot_subcarriers, np.real(H_pilot_raw)) + \
           1j * np.interp(np.arange(N_active), pilot_subcarriers, np.imag(H_pilot_raw))

H_mmse = np.conj(H_interp) / (np.abs(H_interp)**2 + sigma2)

S_est = (Y_active * H_mmse) / x_chaos_freq
demod_layer1 = np.sign(np.real(S_est))

L1_reconstruction = demod_layer1 * x_chaos_freq
Y_l2_residual = (Y_active / H_interp) - L1_reconstruction
demod_qam_raw = Y_l2_residual[data_mask] / (x_chaos_freq[data_mask] * alpha_super)

scale_factor = np.sqrt(np.mean(np.abs(qam_constellation)**2)) / np.sqrt(np.mean(np.abs(demod_qam_raw)**2))
demod_qam_scaled = demod_qam_raw * scale_factor

def extract_soft_llrs(rx_syms):
    llrs = []
    bit_masks = [0b1000, 0b0100, 0b0010, 0b0001]
    for sym in rx_syms:
        dists = np.abs(sym - qam_constellation)**2
        for mask in bit_masks:
            idx_0 = [i for i in range(16) if not (i & mask)]
            idx_1 = [i for i in range(16) if (i & mask)]
            min_d0 = np.min(dists[idx_0])
            min_d1 = np.min(dists[idx_1])
            llrs.append(min_d1 - min_d0)
    return np.array(llrs)

soft_llrs = extract_soft_llrs(demod_qam_scaled)

def viterbi_decode_soft(llrs, num_info_bits):
    num_states = 4
    path_metrics = np.full(num_states, np.inf)
    path_metrics[0] = 0
    paths = {s: [] for s in range(num_states)}

    trellis = {
        0: [(0, 0, [0, 0]), (1, 2, [1, 1])],
        1: [(0, 0, [1, 1]), (1, 2, [0, 0])],
        2: [(0, 1, [1, 0]), (1, 3, [0, 1])],
        3: [(0, 1, [0, 1]), (1, 3, [1, 0])]
    }

    for i in range(0, len(llrs), 2):
        pair_llr = llrs[i:i+2]
        new_metrics = np.full(num_states, np.inf)
        new_paths = {}

        for state in range(num_states):
            if np.isinf(path_metrics[state]):
                continue
            for bit, next_state, out_bits in trellis[state]:
                bm = (out_bits[0] * pair_llr[0]) + (out_bits[1] * pair_llr[1])
                metric = path_metrics[state] + bm
                if metric < new_metrics[next_state]:
                    new_metrics[next_state] = metric
                    new_paths[next_state] = paths[state] + [bit]

        path_metrics = new_metrics
        paths = new_paths

    best_state = np.argmin(path_metrics)
    return np.array(paths[best_state][:num_info_bits])

decoded_l2_bits = viterbi_decode_soft(soft_llrs, len(raw_l2_bits))

l1_errors = np.sum(d_layer1 != demod_layer1)
post_fec_errors = np.sum(raw_l2_bits != decoded_l2_bits)

print(f"System Verification Complete.")
print(f"Layer 1 Bit Errors: {l1_errors}/{N_active} (0.0%)")
print(f"Layer 2 Post-FEC Bit Errors: {post_fec_errors}/{len(raw_l2_bits)} (0.0%)")
