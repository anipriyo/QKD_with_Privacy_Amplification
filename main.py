
import numpy as np
from quantum_operations import encode, decode, run_circuit
from key_processing import privacy_amp, remove_garbage
from security import eve, noise, detect_eavesdropping
from BB84ErrorCorrection import BB84ErrorCorrection

def main():
    n = 100
    ec = BB84ErrorCorrection()
    # Generate initial key
    key = np.random.randint(2, size=int((3*n)/2))
    privacyamplifiedkey = privacy_amp(key)
    print(f"Initial key : {privacyamplifiedkey}")
    # Encode the key
    sharedkey = ec.encode_key(privacyamplifiedkey)
    print(f"length of shared key : {len(sharedkey)}")
    m=len(sharedkey)
    # Sender's basis
    sender_basis = np.random.randint(2, size=len(sharedkey))
    print(f"Sender basis : {sender_basis}")
    # Encode quantum states
    publickey = encode(sharedkey, sender_basis,m)
    print(f"Public key length : {len(publickey)}")
    # Simulate Eve's intervention (0 means no intervention)
    intercepted_publickey = eve(m,publickey, 0.1)
    
    # Add noise (0 means no noise)
    received_publickey = noise(intercepted_publickey, 0.1)
    
    # Receiver's operations
    receiver_basis_guess = np.random.randint(2, size=len(received_publickey))
    print(f"Receiver basis : {receiver_basis_guess}")
    decodedkey = decode(received_publickey, receiver_basis_guess,m)
    print(f"Decoded key : {decodedkey}")
    # Process keys
    
    receiver_key =ec.decode_key(decodedkey)
    print(f"Error Positions : {ec.identify_errors(decodedkey)}")
    print(f"Receiver key (Error corrected): {receiver_key}")
    # receiver_key = remove_garbage(sender_basis, receiver_basis_guess, decodedkey)
    # sender_key = remove_garbage(sender_basis, receiver_basis_guess, sharedkey)
    sender_key=privacyamplifiedkey
    # Convert to list of integers for comparison
    # sender_key = [int(x) for x in sender_key]
    
    # Check results
    if len(receiver_key) == len(sender_key):
        matches = sum(r == s for r, s in zip(receiver_key, sender_key))
        match_rate = matches / len(sender_key)
        print(f"Keys match rate: {match_rate:.2f}")
        print(f"Number of matching bits: {matches} out of {len(sender_key)}")
    else:
        print(f"Key lengths do not match: {len(receiver_key)} vs {len(sender_key)}")
    
    # Check for eavesdropping
    error_rate, alice_final, bob_final = detect_eavesdropping(sender_key, receiver_key)
    print(f"Detected error rate: {error_rate:.2f}")
    print(f"Final key length: {len(alice_final)}")

if __name__ == "__main__":
    main()
