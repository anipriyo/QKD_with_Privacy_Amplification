import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def encode(bits, basis, n):
    publickey = []
    for i in range(n):
        qc = QuantumCircuit(1, 1)
        if basis[i] == 0:  # z basis encoding 0=0 and 1=1
            if bits[i] == 0:
                pass
            else:
                qc.x(0)
        else:  # x basis encoding 0= |+> and 1= |->
            if bits[i] == 0:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)
        qc.barrier()
        publickey.append(qc)
    return publickey


def decode(msg, basis, n):
    measurements = []
    for q in range(n):
        if basis[q] == 0:
            msg[q].measure(0, 0)
        if basis[q] == 1:
            msg[q].h(0)
            msg[q].measure(0, 0)
        counts = run_circuit(msg[q], shots=1)
        measured_bit = next(iter(counts))
        measurements.append(int(measured_bit))
    return measurements


def run_circuit(circuit, shots=1):
    simulator = AerSimulator()
    transpiled_circuit = transpile(circuit, simulator)
    result = simulator.run(transpiled_circuit, shots=shots).result()
    counts = result.get_counts()
    return counts
