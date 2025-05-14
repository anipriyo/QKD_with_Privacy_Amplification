
import numpy as np
from quantum_operations import encode, decode, run_circuit
from key_processing import privacy_amp, remove_garbage , recover_key_with_seed
from security import eve, noise
from BB84ErrorCorrection import BB84ErrorCorrection

def main():
    print("\n=== BB84 Quantum Key Distribution Protocol Demonstration ===\n")
    
    n = 20
    ec = BB84ErrorCorrection()
    
    print("Step 1: Initial Key Generation")
    print("-" * 50)
    # key = np.random.randint(2, size=int((3*n)/2))
    key=[1, 0 ,0 ,1 ,0 ,0 ,1 ,1 ,1 ,0 ,0 ,0, 0, 0 ,1 ,1, 0 ,0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1]

    
    key_str = '[' + ' '.join(str(bit) for bit in key) + ']'
    print(f"Initial non privacy amplified key: {key_str}\n")
    
    privacyamplifiedkey = privacy_amp(key)
    
    print(f"Privacy Amplified key length: {len(privacyamplifiedkey)} bits")
    key_str = '[' + ' '.join(str(bit) for bit in privacyamplifiedkey) + ']'
    print(f"Initial privacy amplified key: {key_str}\n")
    
    print("Step 2: Quantum State Preparation")
    print("-" * 50)
    sharedkey = ec.encode_key(privacyamplifiedkey)
    print(f"Encoded(for css error correction) quantum state length: {len(sharedkey)} qubits")
    
    m = len(sharedkey)
    sender_basis = np.random.randint(2, size=len(sharedkey))
    print(f"Alice's basis choice: {sender_basis}\n")
    
    publickey = encode(sharedkey, sender_basis, m)
    
    print("Step 3: Quantum Channel Transmission")
    print("-" * 50)
    # Simulate Eve's intervention
    intercepted_publickey = eve(m, publickey, 0.05)
    
    received_publickey = noise(intercepted_publickey, 0.05)
    print("Simulated channel conditions:")
    print("- Eavesdropping rate: 5%")
    print("- Channel noise rate: 5%\n")
    
    print("Step 4: Measurement and Key Recovery")
    print("-" * 50)
    receiver_basis_guess = np.random.randint(2, size=len(received_publickey))
    print(f"Bob's basis choice: {receiver_basis_guess}")
    
    decodedkey = decode(received_publickey, receiver_basis_guess, m)
    decoded_str = '[' + ' '.join(str(bit) for bit in decodedkey) + ']'
    print(f"Raw decoded key: {decoded_str}\n")
    
    print("Step 5: Error Detection and Correction")
    print("-" * 50)
    receiver_key = ec.decode_key(decodedkey)
    error_positions = ec.identify_errors(decodedkey)
    error_str = '[' + ' '.join(str(bit) for bit in error_positions) + ']'
    print(f"Detected errors at positions: {error_str}")
    print(f"Total errors detected: {len(error_positions)}\n")
    
    sender_key = privacyamplifiedkey
    
    print("Step 6: Final Key Analysis")
    print("-" * 50)
    if len(receiver_key) == len(sender_key):
        matches = sum(r == s for r, s in zip(receiver_key, sender_key))
        match_rate = matches / len(sender_key)
        print(f"Final key length: {len(sender_key)} bits")
        print(f"Bit match rate: {match_rate:.2%}")
        print(f"Successfully matched bits: {matches} out of {len(sender_key)}")
        print(f"Final key: {receiver_key}")
        key_str = '[' + ' '.join(str(bit) for bit in sender_key) + ']'
        print(f"Init key : {key_str}\n")
    else:
        print("Error: Key lengths do not match")
        print(f"Sender key length: {len(sender_key)}")
        print(f"Receiver key length: {len(receiver_key)}")

    recovered_key = recover_key_with_seed(receiver_key, 1)
    print(f"Recovered key: {recovered_key}")
        
    


if __name__ == "__main__":
    main()
