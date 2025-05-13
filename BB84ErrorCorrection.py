import numpy as np

class CSSCode:
    def __init__(self):
        # CSS code parameters
        self.n1 = 7  # Length of first code
        self.k1 = 4  # Dimension of first code

        # Generator matrices for CSS code
        self.G1 = np.array([
            [1, 1, 0, 1, 0, 0, 0],
            [0, 1, 1, 0, 1, 0, 0],
            [0, 0, 1, 1, 0, 1, 0],
            [0, 0, 0, 1, 1, 0, 1]
        ])

        # Parity check matrices
        self.H1 = np.array([
            [1, 0, 1, 0, 1, 0, 1],
            [0, 1, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1]
        ])

    def encode_block(self, data):
        """Encode a block of data using CSS code"""
        if len(data) != self.k1:
            raise ValueError(f"Data block must be {self.k1} bits")
        return np.mod(np.dot(data, self.G1), 2)

    def decode_block(self, received):
        """Decode a block using CSS syndrome decoding"""
        if len(received) != self.n1:
            raise ValueError(f"Received block must be {self.n1} bits")

        syndrome = np.mod(np.dot(self.H1, received), 2)

        # Error correction based on syndrome
        error_pattern = np.zeros(self.n1, dtype=int)
        syndrome_int = int(''.join(map(str, syndrome)), 2)

        if syndrome_int > 0:
            # Simple lookup for error correction
            for i in range(self.n1):
                test_error = np.zeros(self.n1, dtype=int)
                test_error[i] = 1
                if int(''.join(map(str, np.mod(np.dot(self.H1, test_error), 2))), 2) == syndrome_int:
                    error_pattern = test_error
                    break

        corrected = np.mod(received + error_pattern, 2)
        return corrected[:self.k1]  # Return only the data bits

class BB84ErrorCorrection:
    def __init__(self):
        self.css = CSSCode()

    def _pad_key(self, key):
        """Pad key to match block size"""
        block_size = self.css.k1
        if len(key) % block_size != 0:
            padding_length = block_size - (len(key) % block_size)
            return np.pad(key, (0, padding_length), 'constant')
        return key

    def encode_key(self, key):
        """Encode a key of arbitrary length"""
        padded_key = self._pad_key(key)
        # Convert list to numpy array before reshaping
        padded_key = np.array(padded_key)
        blocks = padded_key.reshape(-1, self.css.k1)
        encoded_blocks = [self.css.encode_block(block) for block in blocks]
        return np.concatenate(encoded_blocks)

    def decode_key(self, received_key):
        """Decode and correct errors in received key"""
        received_key = np.array(received_key)  # Convert list to NumPy array
        blocks = received_key.reshape(-1, self.css.n1)
        decoded_blocks = [self.css.decode_block(block) for block in blocks]
        decoded_key = np.concatenate(decoded_blocks)
        return decoded_key[:len(received_key)]

    def identify_errors(self, received_key):
        """Identify error positions in received key"""
        blocks = received_key.reshape(-1, self.css.n1)
        error_positions = []

        for i, block in enumerate(blocks):
            syndrome = np.mod(np.dot(self.css.H1, block), 2)
            if np.any(syndrome):
                # Calculate exact error positions within the block
                block_errors = np.where(np.mod(np.dot(self.css.H1.T, syndrome), 2))[0]
                # Convert to global positions
                global_errors = [i * self.css.n1 + pos for pos in block_errors]
                error_positions.extend(global_errors)

        return sorted(error_positions)

def test_error_correction():
    """Test the error correction with arbitrary key length"""
    # Create test key
    n = 20  # Arbitrary length
    key = np.random.randint(0, 2, n)

    ec = BB84ErrorCorrection()

    # Encode
    encoded = ec.encode_key(key)

    # Simulate errors
    received = encoded.copy()
    error_pos = np.random.choice(len(encoded), size=int(len(encoded)*0.1), replace=False)
    for pos in error_pos:
        received[pos] = 1 - received[pos]

    # Decode and correct
    decoded = ec.decode_key(received)

    # Calculate error correction success
    success_rate = np.sum(decoded[:n] == key) / n
    print(f"Error correction success rate: {success_rate*100:.2f}%")
    return success_rate

if __name__ == "__main__":
    test_error_correction()