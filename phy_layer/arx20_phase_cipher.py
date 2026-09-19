"""
ARX-20 Cryptographic Physical Layer Security (PLS) Engine
Authors: Abhishek Singh & AI Collaborator
License: MIT
"""

import numpy as np
import struct


class ARX20PhaseCipher:
    def __init__(self, key: bytes, nonce: bytes):
        """
        Initializes the ARX-20 Cryptographic Phase Engine.
        Enforces 32-byte key (256-bit) and 12-byte nonce (96-bit) compliance.
        """
        # Key padding/slicing (256 bits)
        if len(key) < 32:
            key = key.ljust(32, b'\x00')
        else:
            key = key[:32]

        # Nonce padding/slicing (96 bits)
        if len(nonce) < 12:
            nonce = nonce.ljust(12, b'\x00')
        else:
            nonce = nonce[:12]

        self.key = key
        self.nonce = nonce
        self.constants = b"expand 32-byte k"

    def _rotate_left(self, v: int, n: int) -> int:
        return ((v << n) & 0xFFFFFFFF) | (v >> (32 - n))

    def _quarter_round(self, state: list, a: int, b: int, c: int, d: int):
        state[a] = (state[a] + state[b]) & 0xFFFFFFFF
        state[d] ^= state[a]
        state[d] = self._rotate_left(state[d], 16)

        state[c] = (state[c] + state[d]) & 0xFFFFFFFF
        state[b] ^= state[c]
        state[b] = self._rotate_left(state[b], 12)

        state[a] = (state[a] + state[b]) & 0xFFFFFFFF
        state[d] ^= state[a]
        state[d] = self._rotate_left(state[d], 8)

        state[c] = (state[c] + state[d]) & 0xFFFFFFFF
        state[b] ^= state[c]
        state[b] = self._rotate_left(state[b], 7)

    def _arx20_block(self, counter: int) -> bytes:
        constants_words = list(struct.unpack('<4I', self.constants))
        key_words = list(struct.unpack('<8I', self.key))
        nonce_words = list(struct.unpack('<3I', self.nonce))

        initial_state = constants_words + key_words + [counter] + nonce_words
        state = list(initial_state)

        for _ in range(10):
            # Column rounds
            self._quarter_round(state, 0, 4, 8, 12)
            self._quarter_round(state, 1, 5, 9, 13)
            self._quarter_round(state, 2, 6, 10, 14)
            self._quarter_round(state, 3, 7, 11, 15)
            # Diagonal rounds
            self._quarter_round(state, 0, 5, 10, 15)
            self._quarter_round(state, 1, 6, 11, 12)
            self._quarter_round(state, 2, 7, 8, 13)
            self._quarter_round(state, 3, 4, 9, 14)

        out_state = [(state[i] + initial_state[i]) & 0xFFFFFFFF for i in range(16)]
        return struct.pack('<16I', *out_state)

    def generate_phase_sequence(self, num_subcarriers: int, frame_counter: int = 0) -> np.ndarray:
        bytes_needed = num_subcarriers * 4
        keystream = bytearray()
        block_counter = frame_counter

        while len(keystream) < bytes_needed:
            keystream.extend(self._arx20_block(block_counter))
            block_counter += 1

        raw_uint32 = np.frombuffer(keystream[:bytes_needed], dtype=np.uint32)
        phases = (raw_uint32 / 4294967295.0) * 2.0 * np.pi
        return np.exp(1j * phases)
