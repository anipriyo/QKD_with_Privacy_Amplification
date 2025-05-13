
import numpy as np
from qiskit import QuantumCircuit
from quantum_operations import run_circuit



def eve(n,quantum_states, eavesdropping_rate=0.3):
    intercepted_states = []
    eve_basis = np.random.randint(2, size=n)
    # print(eve_basis)

    intercepted_indices = np.random.choice(n, size=int(n * eavesdropping_rate), replace=False)
    print(f"Eve intercepts {len(intercepted_indices)} qubits at positions:", intercepted_indices)

    for i in range(n):
        if i in intercepted_indices:
            eve_circuit = quantum_states[i].copy()
            if eve_basis[i] == 1:
                eve_circuit.h(0)
            eve_circuit.measure(0, 0)
            
            eve_counts = run_circuit(eve_circuit, shots=1)
            eve_result = int(next(iter(eve_counts)))
            
            new_circuit = QuantumCircuit(1, 1)
            if eve_basis[i] == 0:
                if eve_result == 1:
                    new_circuit.x(0)
            else:
                if eve_result == 0:
                    new_circuit.h(0)
                else:
                    new_circuit.x(0)
                    new_circuit.h(0)
            
            new_circuit.barrier()
            intercepted_states.append(new_circuit)
        else:
            intercepted_states.append(quantum_states[i].copy())
    
    return intercepted_states

def noise(quantum_states, noise_rate=0.05):
    noisy_states = []
    for i in range(len(quantum_states)):
        noisy_circuit = quantum_states[i].copy()
        if np.random.random() < noise_rate:
            noise_type = np.random.randint(3)
            if noise_type == 0:
                noisy_circuit.x(0)
            elif noise_type == 1:
                noisy_circuit.z(0)
            else:
                noisy_circuit.y(0)
        noisy_states.append(noisy_circuit)
    return noisy_states

def detect_eavesdropping(alice_bits, bob_bits, sample_size=None):
    if sample_size is None:
        sample_size = min(20, len(bob_bits)//4)
    check_positions = np.random.choice(range(len(bob_bits)), sample_size, replace=False)
    
    alice_sample = [alice_bits[i] for i in check_positions]
    bob_sample = [bob_bits[i] for i in check_positions]
    
    errors = sum(a != b for a, b in zip(alice_sample, bob_sample))
    error_rate = errors / sample_size
    
    remaining_positions = [i for i in range(len(bob_bits)) if i not in check_positions]
    alice_final = [alice_bits[i] for i in remaining_positions]
    bob_final = [bob_bits[i] for i in remaining_positions]
    
    return error_rate, alice_final, bob_final
