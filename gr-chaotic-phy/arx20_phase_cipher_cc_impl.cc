/*
 * gr-chaotic-phy: GNU Radio C++ OOT Module
 * Author: Abhishek Singh
 * License: GPL v3 / MIT
 */

#include "arx20_phase_cipher_cc_impl.h"
#include <gnuradio/io_signature.h>
#include <cmath>
#include <cstdint>

namespace gr {
namespace chaotic_phy {

arx20_phase_cipher_cc::sptr
arx20_phase_cipher_cc::make(const std::string &key, const std::string &nonce, bool decrypt)
{
    return gnuradio::make_block_sptr<arx20_phase_cipher_cc_impl>(key, nonce, decrypt);
}

arx20_phase_cipher_cc_impl::arx20_phase_cipher_cc_impl(
    const std::string &key, const std::string &nonce, bool decrypt)
    : gr::sync_block("arx20_phase_cipher_cc",
                     gr::io_signature::make(1, 1, sizeof(gr_complex)),
                     gr::io_signature::make(1, 1, sizeof(gr_complex))),
      d_decrypt(decrypt),
      d_counter(0)
{
    // Enforce 32-byte key and 12-byte nonce
    std::string k = key; k.resize(32, '0');
    std::string n = nonce; n.resize(12, '0');
    
    std::memcpy(d_key, k.data(), 32);
    std::memcpy(d_nonce, n.data(), 12);
}

inline uint32_t rotl(uint32_t v, int n) { return (v << n) | (v >> (32 - n)); }

void arx20_phase_cipher_cc_impl::quarter_round(uint32_t &a, uint32_t &b, uint32_t &c, uint32_t &d) {
    a += b; d ^= a; d = rotl(d, 16);
    c += d; b ^= c; b = rotl(b, 12);
    a += b; d ^= a; d = rotl(d, 8);
    c += d; b ^= c; b = rotl(b, 7);
}

int arx20_phase_cipher_cc_impl::work(
    int noutput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star &output_items)
{
    const gr_complex *in = (const gr_complex *)input_items[0];
    gr_complex *out = (gr_complex *)output_items[0];

    uint32_t a = 0x61707865, b = 0x3320646e, c = 0x79203233, d = 0x6b206574;

    for (int i = 0; i < noutput_items; ++i) {
        quarter_round(a, b, c, d);
        float phase_angle = (static_cast<float>(a) / 4294967295.0f) * 2.0f * M_PI;
        
        if (d_decrypt) {
            phase_angle = -phase_angle; // Conjugate phase shift for receiver decryption
        }

        gr_complex phase_shift(std::cos(phase_angle), std::sin(phase_angle));
        out[i] = in[i] * phase_shift;
    }

    return noutput_items;
}

} // namespace chaotic_phy
} // namespace gnuradio
