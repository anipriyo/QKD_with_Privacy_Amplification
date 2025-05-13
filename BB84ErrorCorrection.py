import numpy as np

class HammingErrorCorrection:
    """
    Implementation of [7,4,3] Hamming code for error correction in BB84 protocol.
    This code can detect and correct 1-bit errors in each 7-bit block.
    """
    def __init__(self):
        # Generator matrix for [7,4,3] Hamming code
        self.G = np.array([
            [1, 0, 0, 0, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1],
            [0, 0, 1, 0, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1]
        ])

        # Parity-check matrix
        self.H = np.array([
            [1, 1, 0, 1, 1, 0, 0],
            [1, 0, 1, 1, 0, 1, 0],
            [0, 1, 1, 1, 0, 0, 1]
        ])

        # Syndrome to error position mapping
        self.syndrome_table = {
            (0, 0, 0): -1,     # No error
            (1, 1, 0): 0,      # Error in bit 0
            (1, 0, 1): 1,      # Error in bit 1
            (0, 1, 1): 2,      # Error in bit 2
            (1, 1, 1): 3,      # Error in bit 3
            (1, 0, 0): 4,      # Error in bit 4
            (0, 1, 0): 5,      # Error in bit 5
            (0, 0, 1): 6       # Error in bit 6
        }

    def encode_block(self, data_block):
        """
        Encode a 4-bit data block into a 7-bit codeword

        Args:
            data_block: A 4-bit numpy array or list

        Returns:
            7-bit encoded codeword
        """
        if len(data_block) != 4:
            raise ValueError("Data block must be 4 bits")

        data_block = np.array(data_block)
        return np.mod(np.dot(data_block, self.G), 2)

    def decode_block(self, received_block):
        """
        Decode a 7-bit codeword, correcting up to 1 error

        Args:
            received_block: A 7-bit numpy array or list

        Returns:
            Decoded 4-bit data block
        """
        if len(received_block) != 7:
            raise ValueError("Received block must be 7 bits")

        received_block = np.array(received_block)

        # Calculate syndrome
        syndrome = np.mod(np.dot(self.H, received_block), 2)
        syndrome_tuple = tuple(syndrome)

        # Correct error if detected
        error_pos = self.syndrome_table.get(syndrome_tuple, -2)
        corrected_block = received_block.copy()

        if error_pos >= 0:
            # Flip the bit at the error position
            corrected_block[error_pos] = 1 - corrected_block[error_pos]

        # Extract the 4 data bits (since we use systematic code)
        return corrected_block[:4]


class BB84ErrorCorrection:
    """
    Error correction mechanism for BB84 protocol using Hamming codes
    for a 100-bit key.
    """
    def __init__(self):
        self.hamming = HammingErrorCorrection()

    def encode_key(self, key):
        """
        Encode a key for error correction

        Args:
            key: A binary key (list or numpy array of 0s and 1s)

        Returns:
            Encoded key and parity info for error correction
        """
        # Ensure key is of correct length
        if len(key) != 100:
            raise ValueError("Key must be 100 bits long")

        # Convert to numpy array if not already
        key = np.array(key)

        # We'll use Hamming code in blocks 
        # Split into 25 blocks of 4 bits
        blocks = [key[i:i+4] for i in range(0, 100, 4)]

        # Encode each block
        encoded_blocks = [self.hamming.encode_block(block) for block in blocks]

        # The encoded key will be longer (25 blocks * 7 bits = 175 bits)
        encoded_key = np.concatenate(encoded_blocks)

        return encoded_key

    def decode_key(self, received_key):
        """
        Decode and correct errors in a received key

        Args:
            received_key: The received key with possible errors

        Returns:
            Corrected key of 100 bits
        """
        # Check length
        if len(received_key) != 175:  # 25 blocks * 7 bits
            raise ValueError("Received key must be 175 bits long")

        # Convert to numpy array if not already
        received_key = np.array(received_key)

        # Split into blocks of 7 bits
        blocks = [received_key[i:i+7] for i in range(0, 175, 7)]

        # Decode each block
        decoded_blocks = [self.hamming.decode_block(block) for block in blocks]

        # Combine decoded blocks
        corrected_key = np.concatenate(decoded_blocks)

        return corrected_key

    def identify_errors(self, received_key):
        """
        Identify errors in received key

        Args:
            received_key: The received key with possible errors

        Returns:
            List of positions where errors were detected
        """
        # Check length
        if len(received_key) != 175:  # 25 blocks * 7 bits
            raise ValueError("Received key must be 175 bits long")

        error_positions = []

        # Split into blocks of 7 bits
        blocks = [received_key[i:i+7] for i in range(0, 175, 7)]

        for i, block in enumerate(blocks):
            # Calculate syndrome
            syndrome = np.mod(np.dot(self.hamming.H, block), 2)
            syndrome_tuple = tuple(syndrome)

            # Check if error is detected
            if syndrome_tuple != (0, 0, 0):
                error_pos = self.hamming.syndrome_table.get(syndrome_tuple, -2)
                if error_pos >= 0:
                    # Record global position of error
                    global_pos = i * 7 + error_pos
                    error_positions.append(global_pos)

        return error_positions


# Example usage
def example_bb84_error_correction():
    # Create a random 100-bit key
    original_key = np.random.randint(0, 2, 100)

    # Initialize error correction
    ec = BB84ErrorCorrection()

    # Encode the key
    encoded_key = ec.encode_key(original_key)

    # Simulate transmission errors (flip 5 random bits)
    received_key = encoded_key.copy()
    error_positions = np.random.choice(len(encoded_key), 5, replace=False)
    for pos in error_positions:
        received_key[pos] = 1 - received_key[pos]

    print(f"Original key length: {len(original_key)}")
    print(f"Encoded key length: {len(encoded_key)}")
    print(f"Introduced errors at positions: {error_positions}")

    # Identify errors
    detected_errors = ec.identify_errors(received_key)
    print(f"Detected errors at positions: {detected_errors}")

    # Correct errors and decode
    corrected_key = ec.decode_key(received_key)

    # Check if correction worked
    errors_remaining = sum(original_key[i] != corrected_key[i] for i in range(len(original_key)))
    print(f"Errors remaining after correction: {errors_remaining}")

    # Calculate error correction success rate
    if errors_remaining == 0:
        print("Error correction was 100% successful!")
    else:
        print(f"Error correction was {(1 - errors_remaining/len(original_key))*100:.2f}% successful")


# For more complex error patterns, you might need a more sophisticated approach
class EnhancedBB84ErrorCorrection:
    """
    Enhanced error correction for BB84 using cascading approach with Hamming codes 
    and additional parity checks.
    """
    def __init__(self):
        self.base_correction = BB84ErrorCorrection()

    def encode_with_additional_parity(self, key):
        """
        Encode key with Hamming codes and add additional parity bits
        for increased error detection capability
        """
        # First, apply base Hamming encoding
        encoded_key = self.base_correction.encode_key(key)

        # Add global parity bits (one for each 25-bit segment)
        parity_bits = []
        for i in range(0, 100, 25):
            segment = key[i:i+25]
            parity = sum(segment) % 2
            parity_bits.append(parity)

        # Return both the encoded key and the parity bits
        return encoded_key, np.array(parity_bits)

    def correct_errors(self, received_key, parity_bits):
        """
        Apply cascading error correction approach
        """
        # First round: Apply Hamming code correction
        corrected_key = self.base_correction.decode_key(received_key)

        # Second round: Use parity bits to detect if any errors remain
        # This would require a more complex implementation for actual correction

        # For a real implementation, you would use the parity bits to determine
        # which segments might still have errors and apply additional correction

        return corrected_key


if __name__ == "__main__":
    example_bb84_error_correction()