import numpy as np
from functools import reduce

class DeviceSimulator:
    def __init__(self, device, circuit):
        self.device = device
        self.circuit = circuit
        self.gate_info = {g[0]: {"Error rate": g[1]/100, "Delay": g[2]} for g in self.device.gates}
        self.single_qubit_matrices = {
            "x": np.array([[0, 1], [1, 0]], dtype=complex),
            "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
            "z": np.array([[1, 0], [0, -1]], dtype=complex),
            "h": 1/np.sqrt(2) * np.array([[1, 1], [1, -1]], dtype=complex),
            "s": np.array([[1, 0], [0, 1j]], dtype=complex),
            "t": np.array([[1, 0], [0, np.exp(1j*np.pi/4)]], dtype=complex),
            "i": np.eye(2, dtype=complex),
            "measure": np.eye(2, dtype=complex)
        }
        self.two_qubit_matrices = two_qubit_matrices = {
            "CNOT": np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0]
            ], dtype=complex),

            "CZ": np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, -1]
            ], dtype=complex),

            "SWAP": np.array([
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1]
            ], dtype=complex),

            "CPhase(pi/2)": np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1j]
            ], dtype=complex),

            "CPhase(pi/4)": np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, np.exp(1j*np.pi/4)]
            ], dtype=complex)
        }

    def lift_single_qubit_gate(self, gate_matrix, target):
        operations = [np.eye(2, dtype=complex) for _ in range(self.circuit.num_qubits)]
        operations[target] = gate_matrix
        return reduce(np.kron, operations)
    
    def apply_gate_with_bitflip(self, rho, gate_matrix, target):
        p_error = self.gate_info[gate_matrix]["Error rate"]

        G_full = self.lift_single_qubit_gate(self.single_qubit_matrices[gate_matrix], target)
        X_full = self.lift_single_qubit_gate(self.single_qubit_matrices["x"], target)

        K0 = np.sqrt(1 - p_error) * G_full
        K1 = np.sqrt(p_error) * X_full @ G_full

        return K0 @ rho @ K0.conj().T + K1 @ rho @ K1.conj().T
    
    def simulate_circuit(self, shots):
        dim = 2**self.circuit.num_qubits
        rho = np.zeros((dim, dim), dtype=complex)
        rho[0, 0] = 1.0

        for gate in self.circuit.gates:
            if gate.name in self.single_qubit_matrices:
                rho = self.apply_gate_with_bitflip(rho, gate.name, gate.qubits[0])

        self.simulate_measurements(rho, shots)

    def simulate_measurements(self, rho, shots):
        probabilities = np.real(np.diag(rho))
        
        states = np.arange(2**self.circuit.num_qubits)

        print(states)
        print(probabilities)
        
        outcomes = np.random.choice(states, size=shots, p=probabilities)
        outcomes_str = [format(o, f'0{self.circuit.num_qubits}b') for o in outcomes]
        
        counts = {}
        for o in outcomes_str:
            counts[o] = counts.get(o, 0) + 1
        
        counts = self.remap_measurements(counts)

        print(counts)
        return counts

    def remap_measurements(self, counts):
        new_counts = {}

        for bitstring, c in counts.items():
            bits = list(bitstring)
            new_bits = ['0'] * self.circuit.num_qubits

            for logical_idx, physical_idx in self.device.logical_to_physical_mapping.items():
                new_bits[logical_idx] = bits[physical_idx]

            new_bitstring = ''.join(new_bits)
            new_counts[new_bitstring] = new_counts.get(new_bitstring, 0) + c

            new_counts = dict(sorted(new_counts.items(), key=lambda item: int(item[0], 2)))

        return new_counts


