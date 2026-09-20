"""
6G Physical Layer Security & ISAC Radar End-to-End Master Simulation
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import numpy as np
from phy_layer.arx20_phase_cipher import ARX20PhaseCipher
from phy_layer.chaos_spreader import ChaosSpreader
from subsystems.isac_radar import ISACRadarEngine


def run_end_to_end_simulation():
    print("=================================================================")
    print("--- 6G Physical Layer Security & ISAC Master Simulation Run ---")
    print("=================================================================\n")

    # -------------------------------------------------------------------
    # Configuration Parameters
    # -------------------------------------------------------------------
    num_subcarriers = 128
    num_frames = 256
    snr_db = 15.0  # Signal-to-Noise Ratio (dB)
    target_range_m = 45.0
    target_velocity_kmh = 72.0
    target_velocity_mps = target_velocity_kmh / 3.6

    key = b"6G_CHAOTIC_SUPERPOSITION_KEY_32B"
    nonce = b"NYC_RF_NONCE"

    # -------------------------------------------------------------------
    # 1. Initialize Engines
    # -------------------------------------------------------------------
    spreader = ChaosSpreader(key=key, nonce=nonce)
    radar_engine = ISACRadarEngine(
        num_subcarriers=num_subcarriers,
        carrier_freq_hz=28e9,
        subcarrier_spacing_hz=120e3
    )

    print("[1/4] Generating 256-Bit ARX-20 Phase Cipher Keystream...")
    arx_phase_seq = spreader.generate_phase_sequence(num_subcarriers, frame_counter=0)
    print(f"      Phase Sequence Shape: {arx_phase_seq.shape}")
    print(f"      Cipher Unit Amplitude Verified: {np.allclose(np.abs(arx_phase_seq), 1.0)}")

    # -------------------------------------------------------------------
    # 2. Transmit Signal Preparation (QPSK + ARX Phase Encryption)
    # -------------------------------------------------------------------
    print("\n[2/4] Modulating Data and Applying Physical Layer Encryption...")
    # Random QPSK symbols
    tx_bits = np.random.randint(0, 2, num_subcarriers * 2)
    tx_symbols = (1 - 2 * tx_bits[::2]) / np.sqrt(2) + 1j * (1 - 2 * tx_bits[1::2]) / np.sqrt(2)

    # Apply ARX-20 Phase Cipher
    tx_cipher_symbols = spreader.apply_chaos(tx_symbols, arx_phase_seq)

    # -------------------------------------------------------------------
    # 3. Communications Channel Processing & Decryption
    # -------------------------------------------------------------------
    print("\n[3/4] Simulating Communication Link over AWGN Channel...")
    snr_linear = 10 ** (snr_db / 10.0)
    noise_std = 1.0 / np.sqrt(2 * snr_linear)
    noise = (np.random.randn(num_subcarriers) + 1j * np.random.randn(num_subcarriers)) * noise_std

    rx_cipher_symbols = tx_cipher_symbols + noise

    # Decrypt using authorized ARX-20 cipher sequence
    rx_symbols = spreader.remove_chaos(rx_cipher_symbols, arx_phase_seq)

    # Demodulate QPSK
    rx_bits_i = (np.real(rx_symbols) < 0).astype(int)
    rx_bits_q = (np.imag(rx_symbols) < 0).astype(int)
    rx_bits = np.empty(num_subcarriers * 2, dtype=int)
    rx_bits[::2] = rx_bits_i
    rx_bits[1::2] = rx_bits_q

    bit_errors = np.sum(tx_bits != rx_bits)
    ber = bit_errors / len(tx_bits)

    print(f"      Communication Link SNR: {snr_db} dB")
    print(f"      Bit Error Rate (BER):   {ber:.6f} ({bit_errors}/{len(tx_bits)} bit errors)")

    # -------------------------------------------------------------------
    # 4. Integrated Sensing and Communications (ISAC) Radar Detection
    # -------------------------------------------------------------------
    print("\n[4/4] Executing High-Precision ISAC Radar Backscatter Processing...")
    H_matrix = radar_engine.simulate_radar_backscatter(
        num_frames=num_frames,
        target_range_m=target_range_m,
        target_velocity_mps=target_velocity_mps,
        snr_db=snr_db
    )

    _, est_range, est_velocity_kmh = radar_engine.process_range_doppler_map_high_res(
        H_matrix, n_fft_range=1024, n_fft_doppler=512
    )

    range_error = abs(est_range - target_range_m)
    velocity_error = abs(est_velocity_kmh - target_velocity_kmh)

    print(f"      Ground Truth Target: Range = {target_range_m:.2f} m | Velocity = {target_velocity_kmh:.2f} km/h")
    print(f"      Detected Target:     Range = {est_range:.2f} m | Velocity = {est_velocity_kmh:.2f} km/h")
    print(f"      Radar Errors:        Range Error = {range_error:.2f} m | Velocity Error = {velocity_error:.2f} km/h")

    # -------------------------------------------------------------------
    # Verification Verdict
    # -------------------------------------------------------------------
    print("\n=================================================================")
    if ber == 0.0 and range_error < 0.5:
        print("VERDICT: SUCCESS — Communication BER = 0.0 & Sub-Meter ISAC Accuracy Achieved!")
    else:
        print("VERDICT: CHECK PARAMETERS — Metrics exceeded baseline thresholds.")
    print("=================================================================\n")


if __name__ == "__main__":
    run_end_to_end_simulation()
