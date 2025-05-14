def privacy_amp(key):
    if len(key) < 3:
        print(f"Key too short for privacy amplification ({len(key)} < 3)")
        return key
    compressed_key = []
    for i in range(len(key)):
        if(i+1 < len(key)):
            compressed_key.append(key[i] ^ key[i+1])  # adjacent bit XOR

    return compressed_key


def recover_key(compressed_key, seed_bit):
    recovered_key = []  
    recovered_key.append(seed_bit)
    for i in range(len(compressed_key)):
        recovered_key.append(recovered_key[i] ^ compressed_key[i])
    return recovered_key


def remove_garbage(a_basis, b_basis, bits):
    good_bits = []
    for q in range(len(a_basis)):
        if a_basis[q] == b_basis[q]:
            good_bits.append(bits[q])
    return good_bits
