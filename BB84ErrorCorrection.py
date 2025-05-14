
import numpy as np
from itertools import product

class CSSCode:
    def __init__(self, n1=7, k1=1, k2=3):
        """
        Initialize a CSS code with specified parameters.

        Args:
            n1: Length of the code (default is 7 for Steane code)
            k1: First dimension parameter (default is 1)
            k2: Second dimension parameter (default is 3)
        """
        # CSS code parameters
        self.n1 = n1  # Length of code (default is Steane [[7,1,3]] code)
        self.k1 = k1  # Information qubits (k2-k1)
        self.k2 = k2  # Second dimension parameter

        if n1 == 7 and k1 == 1 and k2 == 3:
            # Use the standard Steane [[7,1,3]] code
            # Generator matrix for C1 (classical code)
            self.G1 = np.array([
                [1, 0, 0, 1, 0, 1, 0],
                [0, 1, 0, 1, 0, 0, 1],
                [0, 0, 1, 0, 1, 1, 1]
            ])

            # Generator matrix for C2 (classical code, C1 ⊂ C2)
            self.G2 = np.array([
                [1, 0, 0, 1, 0, 1, 0],
                [0, 1, 0, 1, 0, 0, 1],
                [0, 0, 1, 0, 1, 1, 1],
                [0, 0, 0, 1, 1, 1, 0]
            ])

            # Parity check matrices
            self.H1 = np.array([
                [0, 0, 0, 1, 1, 1, 0],
                [0, 1, 1, 0, 0, 1, 0],
                [1, 0, 1, 0, 1, 0, 0],
                [1, 1, 0, 1, 0, 0, 0]
            ])

            self.H2 = np.array([
                [0, 0, 0, 1, 1, 1, 0],
                [0, 1, 1, 0, 0, 1, 0],
                [1, 0, 1, 0, 1, 0, 0]
            ])

            # Pre-compute error syndrome lookup table
            self._build_syndrome_table()
        else:
            raise ValueError("Currently only supporting the Steane [[7,1,3]] code (n1=7, k1=1, k2=3)")

    def _build_syndrome_table(self):
        """Build lookup tables for syndrome decoding"""
        # For bit-flip errors (X errors)
        self.x_syndrome_table = {}
        # For phase-flip errors (Z errors)
        self.z_syndrome_table = {}

        # Generate all possible single-bit error patterns
        for i in range(self.n1):
            # Bit flip error at position i
            error = np.zeros(self.n1, dtype=int)
            error[i] = 1

            # Calculate syndrome for bit flip error
            x_syndrome = np.mod(np.dot(self.H2, error), 2)
            x_syndrome_key = self._syndrome_to_key(x_syndrome)
            self.x_syndrome_table[x_syndrome_key] = error

            # Calculate syndrome for phase flip error
            z_syndrome = np.mod(np.dot(self.H1, error), 2)
            z_syndrome_key = self._syndrome_to_key(z_syndrome)
            self.z_syndrome_table[z_syndrome_key] = error

        # Also add no-error case
        zero_error = np.zeros(self.n1, dtype=int)
        self.x_syndrome_table[self._syndrome_to_key(np.zeros(len(self.H2), dtype=int))] = zero_error
        self.z_syndrome_table[self._syndrome_to_key(np.zeros(len(self.H1), dtype=int))] = zero_error

        # Add capability to correct some two-bit errors
        for i, j in product(range(self.n1), range(i+1, self.n1)):
            error = np.zeros(self.n1, dtype=int)
            error[i] = error[j] = 1

            # Calculate syndrome for bit flip error
            x_syndrome = np.mod(np.dot(self.H2, error), 2)
            x_syndrome_key = self._syndrome_to_key(x_syndrome)

            # Only add if this syndrome isn't already mapped to a single-bit error
            if x_syndrome_key not in self.x_syndrome_table:
                self.x_syndrome_table[x_syndrome_key] = error

            # Calculate syndrome for phase flip error
            z_syndrome = np.mod(np.dot(self.H1, error), 2)
            z_syndrome_key = self._syndrome_to_key(z_syndrome)

            # Only add if this syndrome isn't already mapped to a single-bit error
            if z_syndrome_key not in self.z_syndrome_table:
                self.z_syndrome_table[z_syndrome_key] = error

    def _syndrome_to_key(self, syndrome):
        """Convert syndrome array to integer key for lookup"""
        return int(''.join(map(str, syndrome)), 2)

    def encode_block(self, data):
        """
        Encode a block of data using CSS code

        Args:
            data: Input data to encode (should be k2-k1 bits)

        Returns:
            Encoded bit string of length n1
        """
        if len(data) != self.k2 - self.k1:
            raise ValueError(f"Data block must be {self.k2 - self.k1} bits")

        # For Steane code, k2-k1 = 2
        logical_word = np.zeros(3, dtype=int)  # Match G2 dimensions (3,7)
        logical_word[self.k1:] = data

        # Encode using the second classical code C2
        return np.mod(np.dot(logical_word, self.G2), 2)

    def decode_block(self, received):
        """
        Decode a block using CSS syndrome decoding

        Args:
            received: Received noisy codeword of length n1

        Returns:
            Decoded data of length k2-k1
        """
        if len(received) != self.n1:
            raise ValueError(f"Received block must be {self.n1} bits")

        # Calculate syndromes for both bit-flip and phase-flip errors
        x_syndrome = np.mod(np.dot(self.H2, received), 2)
        x_syndrome_key = self._syndrome_to_key(x_syndrome)

        # Look up error pattern in table
        if x_syndrome_key in self.x_syndrome_table:
            error_pattern = self.x_syndrome_table[x_syndrome_key]
        else:
            # If syndrome not in table, use minimum weight error correction
            error_pattern = self._minimum_weight_correction(received, self.H2)

        # Apply error correction
        corrected = np.mod(received + error_pattern, 2)

        # Decode by extracting information bits
        # For Steane code with k2-k1=2, we need to extract the logical bits
        # This is done by projecting onto the logical subspace
        logical_bits = np.zeros(self.k2 - self.k1, dtype=int)

        # For Steane code specifically, we can extract the logical bits
        # using these specific bit positions
        if self.n1 == 7:
            logical_bits[0] = corrected[3]
            logical_bits[1] = corrected[5]

        return logical_bits

    def _minimum_weight_correction(self, received, H):
        """
        Find minimum weight error pattern matching the syndrome

        Args:
            received: Received noisy codeword
            H: Parity check matrix

        Returns:
            Error pattern with minimum weight
        """
        syndrome = np.mod(np.dot(H, received), 2)

        # Try all error patterns of weight 1
        for i in range(self.n1):
            error = np.zeros(self.n1, dtype=int)
            error[i] = 1
            if np.array_equal(np.mod(np.dot(H, error), 2), syndrome):
                return error

        # Try all error patterns of weight 2
        for i in range(self.n1):
            for j in range(i+1, self.n1):
                error = np.zeros(self.n1, dtype=int)
                error[i] = error[j] = 1
                if np.array_equal(np.mod(np.dot(H, error), 2), syndrome):
                    return error

        # If no exact match, return zero error (best guess)
        return np.zeros(self.n1, dtype=int)


class BB84ErrorCorrection:
    def __init__(self):
        """Initialize with Steane [[7,1,3]] CSS code"""
        self.css = CSSCode()  # Default to Steane code
        self.effective_k = self.css.k2 - self.css.k1  # Effective message length per block

    def _pad_key(self, key):
        """
        Pad key to match block size

        Args:
            key: Original key as array or list

        Returns:
            Padded key with length divisible by effective_k
        """
        key = np.array(key, dtype=int)
        block_size = self.effective_k
        if len(key) % block_size != 0:
            padding_length = block_size - (len(key) % block_size)
            return np.pad(key, (0, padding_length), 'constant')
        return key

    def encode_key(self, key):
        """
        Encode a key of arbitrary length

        Args:
            key: Original key to encode

        Returns:
            Encoded key with error correction
        """
        padded_key = self._pad_key(key)
        # Convert list to numpy array before reshaping
        padded_key = np.array(padded_key)
        blocks = padded_key.reshape(-1, self.effective_k)
        encoded_blocks = [self.css.encode_block(block) for block in blocks]
        return np.concatenate(encoded_blocks)

    def decode_key(self, received_key):
        """
        Decode and correct errors in received key

        Args:
            received_key: Received key with possible errors

        Returns:
            Decoded and error-corrected key
        """
        received_key = np.array(received_key)  # Convert list to NumPy array
        original_length = len(received_key)

        # Ensure the key length is divisible by n1
        n1 = self.css.n1
        if len(received_key) % n1 != 0:
            # Pad with zeros if needed
            padding_length = n1 - (len(received_key) % n1)
            received_key = np.pad(received_key, (0, padding_length), 'constant')

        # Split into blocks of length n1
        blocks = received_key.reshape(-1, n1)

        # Decode each block
        decoded_blocks = [self.css.decode_block(block) for block in blocks]

        # Concatenate all blocks and trim to original length
        return np.concatenate(decoded_blocks)[:original_length]

    def identify_errors(self, received_key):
        """
        Identify error positions in received key

        Args:
            received_key: Received key with possible errors

        Returns:
            List of positions where errors were detected
        """
        received_key = np.array(received_key)  # Convert list to NumPy array

        # Ensure the key length is divisible by n1
        n1 = self.css.n1
        original_length = len(received_key)
        if len(received_key) % n1 != 0:
            # Pad with zeros if needed
            padding_length = n1 - (len(received_key) % n1)
            received_key = np.pad(received_key, (0, padding_length), 'constant')

        blocks = received_key.reshape(-1, n1)
        error_positions = []

        for i, block in enumerate(blocks):
            # Calculate syndrome
            x_syndrome = np.mod(np.dot(self.css.H2, block), 2)
            x_syndrome_key = self.css._syndrome_to_key(x_syndrome)

            # Skip if no error detected
            if x_syndrome_key == 0:
                continue

            # Get error pattern
            if x_syndrome_key in self.css.x_syndrome_table:
                error_pattern = self.css.x_syndrome_table[x_syndrome_key]
            else:
                # Use minimum weight correction
                error_pattern = self.css._minimum_weight_correction(block, self.css.H2)

            # Identify error positions within the block
            block_errors = np.where(error_pattern)[0]

            # Convert to global positions
            global_errors = [i * n1 + pos for pos in block_errors if i * n1 + pos < original_length]
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

    # Simulate errors at different rates
    error_rates = [0.05, 0.1, 0.15]
    results = {}

    for rate in error_rates:
        received = encoded.copy()
        error_pos = np.random.choice(len(encoded), size=int(len(encoded)*rate), replace=False)
        for pos in error_pos:
            received[pos] = 1 - received[pos]

        # Identify errors
        detected_errors = ec.identify_errors(received)

        # Decode and correct
        decoded = ec.decode_key(received)[:n]

        # Calculate error correction success
        success_rate = np.sum(decoded == key) / n
        results[rate] = {
            'success_rate': success_rate,
            'detected_errors': len(detected_errors),
            'actual_errors': len(error_pos)
        }
        print(f"Error rate: {rate*100:.1f}%, Success rate: {success_rate*100:.2f}%")
        print(f"Detected {len(detected_errors)} errors out of {len(error_pos)} actual errors")

    return results


if __name__ == "__main__":
    test_error_correction()
