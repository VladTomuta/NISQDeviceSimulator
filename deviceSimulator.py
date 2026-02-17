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
            "cx": np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 0]
            ], dtype=complex),

            "cz": np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, -1]
            ], dtype=complex),

            "swap": np.array([
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1]
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
    
    def lift_two_qubit_gate(self, gate_matrix, targets):
        operations = [np.eye(2, dtype=complex) for _ in range(self.circuit.num_qubits - 1)]
        operations[targets[0]] = gate_matrix

        #print("Rho for lift_two_qubit_gate:")
        #print(operations)
        #print(gate_matrix)
        #print(targets)
        #print(reduce(np.kron, operations))

        #print("Operations:")
        #print(operations)

        return reduce(np.kron, operations)
    
    def swap_qubit_to_a_position(self, rho, start_positon, end_position):
        while start_positon != end_position: 
            swap_gate = self.lift_two_qubit_gate(self.two_qubit_matrices["swap"], [start_positon])
            rho = swap_gate @ rho @ swap_gate.conj().T

            start_positon+=1

        return rho
    
    def reverse_swap_qubit_to_a_position(self, rho, start_positon, end_position):
        while start_positon != end_position: 
            swap_gate = self.lift_two_qubit_gate(self.two_qubit_matrices["swap"], [start_positon -1])
            rho = swap_gate @ rho @ swap_gate.conj().T

            start_positon-=1

        return rho

    def apply_two_qubit_gate_with_bitflip(self, rho, gate_matrix, targets):
        p_error = self.gate_info[gate_matrix]["Error rate"]
        
        #print("\nTargets:")
        #print(targets)

        #Move qubits one next to the other in the density matrix
        if(targets[0] < targets[1]):
            rho = self.swap_qubit_to_a_position(rho, targets[0], targets[1] - 1)
            new_targets_after_swap = [targets[1] - 1, targets[1]]
        else:
            rho = self.swap_qubit_to_a_position(rho, targets[1], targets[0])
            new_targets_after_swap = [targets[0] - 1, targets[0]]
        
        #Apply Gate
        G_full = self.lift_two_qubit_gate(self.two_qubit_matrices[gate_matrix], new_targets_after_swap)
        X_full = self.lift_single_qubit_gate(self.single_qubit_matrices["x"], new_targets_after_swap[1])

        K0 = np.sqrt(1 - p_error) * G_full
        K1 = np.sqrt(p_error) * X_full @ G_full

        rho = K0 @ rho @ K0.conj().T + K1 @ rho @ K1.conj().T

        #print("\nTargets:")
        #print(targets)

        #Move qubits back to the original position
        if(targets[0] < targets[1]):
            rho = self.reverse_swap_qubit_to_a_position(rho, targets[1] - 1, targets[0])
        else:
            rho = self.reverse_swap_qubit_to_a_position(rho, targets[0], targets[1])
        
        return rho

    def simulate_circuit(self, shots):
        dim = 2**self.circuit.num_qubits
        rho = np.zeros((dim, dim), dtype=complex)
        rho[0, 0] = 1.0

        gate_index = 0

        for gate in self.circuit.gates:
            if gate.name in self.single_qubit_matrices:
                rho = self.apply_gate_with_bitflip(rho, gate.name, gate.qubits[0])
            elif gate.name in self.two_qubit_matrices:
                rho = self.apply_two_qubit_gate_with_bitflip(rho, gate.name, gate.qubits)
            else:
                raise ValueError("The gate is unkown for the simulator.")
            
            gate_index += 1
            if gate_index % 1000 == 0:
                print("Step " + str(gate_index) + " out of " + str(len(self.circuit.gates)) + " done.")

        self.simulate_measurements(rho, shots)

    def simulate_measurements(self, rho, shots):
        probabilities = np.real(np.diag(rho))
        probabilities = np.clip(probabilities, 0, None)
        probabilities /= np.sum(probabilities)

        
        states = np.arange(2**self.circuit.num_qubits)

        #print("\nFINAL STATES:")
        #print(rho)

        print("Trace:", np.trace(rho))
        print("Sum diag:", np.sum(np.diag(rho)))
        
        outcomes = np.random.choice(states, size=shots, p=probabilities)
        outcomes_str = [format(o, f'0{self.circuit.num_qubits}b') for o in outcomes]
        
        counts = {}
        for o in outcomes_str:
            counts[o] = counts.get(o, 0) + 1

        #print(counts)
        
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
            new_counts[new_bitstring[::-1]] = new_counts.get(new_bitstring, 0) + c

            new_counts = dict(sorted(new_counts.items(), key=lambda item: int(item[0], 2)))

        return new_counts


