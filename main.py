
import numpy as np
from quantum_operations import encode, decode, run_circuit
from key_processing import privacy_amp, remove_garbage
from security import eve, noise, detect_eavesdropping

def main():
    n = 100
    # Generate initial key
    key = np.random.randint(2, size=int((3*n)/2))
    sharedkey = privacy_amp(key)
    
    # Sender's basis
    sender_basis = np.random.randint(2, size=n)
    
    # Encode quantum states
    publickey = encode(sharedkey, sender_basis)
    
    # Simulate Eve's intervention (0 means no intervention)
    intercepted_publickey = eve(publickey, 0)
    
    # Add noise (0 means no noise)
    received_publickey = noise(intercepted_publickey, 0)
    
    # Receiver's operations
    receiver_basis_guess = np.random.randint(2, size=n)
    decodedkey = decode(received_publickey, receiver_basis_guess)
    
    # Process keys
    receiver_key = remove_garbage(sender_basis, receiver_basis_guess, decodedkey)
    sender_key = remove_garbage(sender_basis, receiver_basis_guess, sharedkey)
    sender_key = [int(x) for x in sender_key]
    
    # Check results
    print("Keys match:", receiver_key == sender_key)
    match_percentage = len(receiver_key) / n * 100
    print(f"Percentage of matching bases: {match_percentage:.2f}%")
    
    # Check for eavesdropping
    error_rate, alice_final, bob_final = detect_eavesdropping(sender_key, receiver_key)
    print(f"Detected error rate: {error_rate:.2f}")
    print(f"Final key length: {len(alice_final)}")

if __name__ == "__main__":
    main()
