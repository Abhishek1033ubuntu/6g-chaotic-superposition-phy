"""
Soft-Decision LLR Demapper & Viterbi Trellis Decoder
Authors: Abhishek Singh & AI Collaborator
"""
import numpy as np

class SoftViterbiFEC:
    def __init__(self, constellation):
        self.constellation = constellation

    def compute_soft_llrs(self, rx_symbols):
        llrs = []
        bit_masks = [0b1000, 0b0100, 0b0010, 0b0001]
        for sym in rx_symbols:
            dists = np.abs(sym - self.constellation)**2
            for mask in bit_masks:
                idx_0 = [i for i in range(16) if not (i & mask)]
                idx_1 = [i for i in range(16) if (i & mask)]
                min_d0 = np.min(dists[idx_0])
                min_d1 = np.min(dists[idx_1])
                llrs.append(min_d1 - min_d0)
        return np.array(llrs)

    def decode(self, llrs, num_info_bits):
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
