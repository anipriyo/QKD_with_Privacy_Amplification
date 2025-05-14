
def privacy_amp(key, bits_per_block=3, leakage_assumption=1):
    if len(key) < bits_per_block:
        print(f"Key too short for privacy amplification ({len(key)} < {bits_per_block})")
        return key

    blocks_count = len(key) // bits_per_block
    compressed_key = []

    for i in range(blocks_count):
        block = key[i*bits_per_block:i*bits_per_block+bits_per_block]

        if len(block) >= 3: 
            compressed_key.append(block[0] ^ block[1])  # x⊕y
            compressed_key.append(block[1] ^ block[2])  # y⊕z

    # original_entropy = len(key)
    # compressed_entropy = len(compressed_key)
    # leaked_entropy = blocks_count * leakage_assumption

    # print(f"Original key length: {original_entropy} bits")
    # print(f"Compressed key length: {compressed_entropy} bits")
    # print(f"Entropy reduction: {original_entropy - compressed_entropy} bits")
    # print(f"Security margin: {compressed_entropy - leaked_entropy} bits")

    return compressed_key


def recover_key_with_seed(compressed_key, seed_bit, bits_per_block=3):
    if not compressed_key:
        return []

    recovered_key = [seed_bit]  
    blocks_count = len(compressed_key) // 2

    for i in range(blocks_count):

        x_xor_y = compressed_key[i*2]
        y_xor_z = compressed_key[i*2+1]


        y = recovered_key[-1] ^ x_xor_y
        recovered_key.append(y)


        z = y ^ y_xor_z
        recovered_key.append(z)

    return recovered_key


def remove_garbage(a_basis, b_basis, bits):
    good_bits = []
    for q in range(len(a_basis)):
        if a_basis[q] == b_basis[q]:
            good_bits.append(bits[q])
    return good_bits
