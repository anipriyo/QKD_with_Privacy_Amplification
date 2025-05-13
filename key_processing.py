
def privacy_amp(key, bits_per_block=3, leakage_assumption=1):
    if len(key) < bits_per_block:
        print(f"Key too short for privacy amplification ({len(key)} < {bits_per_block})")
        return key

    truncate = (len(key) // bits_per_block) * bits_per_block
    truncated_key = key[:truncate]
    compressed_key = []

    for i in range(0, truncate, bits_per_block):
        block = truncated_key[i:i+bits_per_block]
        compressed_key.append(block[0] ^ block[1])  # x xor y
        compressed_key.append(block[1] ^ block[2])  # y xor z

    return compressed_key

def remove_garbage(a_basis, b_basis, bits):
    good_bits = []
    for q in range(len(a_basis)):
        if a_basis[q] == b_basis[q]:
            good_bits.append(bits[q])
    return good_bits
