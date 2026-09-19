"""
ChaCha20 Cryptographic Physical Layer Security (PLS) Engine
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import numpy as np
import struct

class ChaCha20PhaseCipher:
    def __init__(self, key: bytes, nonce: bytes):
        """
        Initializes the ChaCha20 Cryptographic Phase Engine.
        :param key: 32-byte (256-bit) secret key
        :param nonce: 12-byte (96-bit) frame nonce / initialization vector
        """
        assert len(key) == 32, "Key must be exactly 32 bytes (256 bits)"
        assert len(nonce) == 12, "Nonce must be exactly 12 bytes (96 bits)"
        
        self.key = key
        self.nonce = nonce
        self.constants = b"expand 32-byte k"

    def _rotate_left(self, v, n):
        return ((v << n) & 0xFFFFFFFF) | (v >> (32 - n))

    def _quarter_round(self, state, a, b, c, d):
        state[a] = (state[a] + state[b]) & 0xFFFFFFFF; state[d] ^= state[a]; state[d] = self._rotate_left(state[d], 16)
        state[c] = (state[c] + state[d]) & 0xFFFFFFFF; state[b] ^= state[c]; state[b] = self._rotate_left(state[b], 12)
        state[a] = (state[a] + state[b]) & 0xFFFFFFFF; state[d] ^= state[a]; state[d] = self._rotate_left(state[d], 8)
        state[c] = (state[c] + state[d]) & 0xFFFFFFFF; state[b] ^= state[c]; state[b] = self._rotate_left(state[b], 7)

    def _chacha20_block(self, counter: int) -> bytes:
        """
        Generates a 64-byte (512-bit) cryptographic keystream block using 20 rounds of ARX.
        """
        constants_words = list(struct.unpack('<4I', self.constants))
        key_words = list(struct.unpack('<8I', self.key))
        nonce_words = list(struct.unpack('<3I', self.nonce))
        
        initial_state = constants_words + key_words + [counter] + nonce_words
        state = list(initial_state)

        # 20 Rounds (10 iterations of 8 quarter-rounds)
        for _ in range(10):
            # Column rounds
            self._quarter_round(state, 0, 4,  8, 12)
            self._quarter_round(state, 1, 5,  9, 13)
            self._quarter_round(state, 2, 6, 10, 14)
            self._quarter_round(state, 3, 7, 11, 15)
            # Diagonal rounds
            self._quarter_round(state, 0, 5, 10, 15)
            self._quarter_round(state, 1, 6, 11, 12)
            self._quarter_round(state, 2, 7,  8, 13)
            self._quarter_round(state, 3, 4,  9, 14)

        # Add initial state back
        out_state = [(state[i] + initial_state[i]) & 0xFFFFFFFF for i in range(16)]
        return struct.pack('<16I', *out_state)

    def generate_phase_sequence(self, num_subcarriers: int, frame_counter: int = 0) -> np.ndarray:
        """
        Maps continuous ChaCha20 byte streams directly into complex phase vectors e^(j * phi_k).
        """
        bytes_needed = num_subcarriers * 4  # 32 bits per subcarrier phase angle
        keystream = bytearray()
        block_counter = frame_counter

        while len(keystream) < bytes_needed:
            keystream.extend(self._chacha20_block(block_counter))
            block_counter += 1

        # Extract 32-bit uints and map to angles [0, 2*pi)
        raw_uint32 = np.frombuffer(keystream[:bytes_needed], dtype=np.uint32)
        phases = (raw_uint32 / 4294967295.0) * 2.0 * np.pi
        
        # Return complex unit-magnitude phase sequence
        return np.exp(1j * phases)
