import numpy as np

class DeviceSimulator:
    def __init__(self, circuit, apply_error_rates = True, apply_decoherence = True):
        self.circuit = circuit
        self.num_qubits = circuit.num_qubits
        self.apply_error_rates = apply_error_rates
        self.apply_decoherence = apply_decoherence
        self.measured_qubits = []

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

        self.two_qubit_matrices = {
            "cx": np.array([[1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 0, 1],
                            [0, 0, 1, 0]], dtype=complex),
            "cz": np.array([[1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, -1]], dtype=complex),
            "swap": np.array([[1, 0, 0, 0],
                              [0, 0, 1, 0],
                              [0, 1, 0, 0],
                              [0, 0, 0, 1]], dtype=complex)
        }

    def apply_single_qubit_operator(self, rho, operator, qubit):
        rho_tensor = rho.reshape([2]*self.num_qubits*2)

        rho_tensor = np.tensordot(operator, rho_tensor, axes=([1], [qubit]))
        rho_tensor = np.moveaxis(rho_tensor, 0, qubit)

        rho_tensor = np.tensordot(operator.conj(), rho_tensor, axes=([1], [qubit+self.num_qubits]))
        rho_tensor = np.moveaxis(rho_tensor, 0, qubit+self.num_qubits)

        return rho_tensor.reshape((2**self.num_qubits, 2**self.num_qubits))

    def apply_two_qubit_operator(self, rho, operator, q1, q2):
        if q1 > q2:
            q1, q2 = q2, q1
        rho_tensor = rho.reshape([2]*self.num_qubits*2)
        gate_matrix = operator.reshape(2,2,2,2)

        rho_tensor = np.tensordot(gate_matrix, rho_tensor, axes=([2, 3],[q1, q2]))
        rho_tensor = np.moveaxis(rho_tensor, [0, 1], [q1, q2])

        rho_tensor = np.tensordot(gate_matrix.conj(), rho_tensor, axes=([2, 3],[q1+self.num_qubits, q2+self.num_qubits]))
        rho_tensor = np.moveaxis(rho_tensor, [0, 1], [q1+self.num_qubits, q2+self.num_qubits])

        return rho_tensor.reshape((2**self.num_qubits, 2**self.num_qubits))

    def apply_single_qubit_gate_with_bitflip(self, rho, gate_name, qubit):
        error_probability = self.circuit.gate_info[gate_name]["Error rate"]
        if self.apply_error_rates == False:
            error_probability = 0
        gate_matrix = self.single_qubit_matrices[gate_name]

        K0 = np.sqrt(1 - error_probability) * gate_matrix
        K1 = np.sqrt(error_probability) * self.single_qubit_matrices["x"] @ gate_matrix

        rho = self.apply_single_qubit_operator(rho, K0, qubit) + \
              self.apply_single_qubit_operator(rho, K1, qubit)
        return rho

    def apply_two_qubit_gate_with_bitflip(self, rho, gate_name, targets):
        error_probability = self.circuit.gate_info[gate_name]["Error rate"]
        if self.apply_error_rates == False:
            error_probability = 0
        q1, q2 = targets
        rho_clean = self.apply_two_qubit_operator(rho, self.two_qubit_matrices[gate_name], q1, q2)

        rho_flip = self.apply_single_qubit_operator(rho_clean, self.single_qubit_matrices["x"], q1)
        rho_flip = self.apply_single_qubit_operator(rho_clean, self.single_qubit_matrices["x"], q2)

        return (1 - error_probability) * rho_clean + error_probability * rho_flip

    def apply_delay_decoherence(self, rho, idle_qubits, delta_t):
        for q in idle_qubits:
            t1_time = self.circuit.t1_times[q]
            t2_time = self.circuit.t2_times[q]

            p1 = 1 - np.exp(-delta_t/t1_time)
            K0 = np.array([[1, 0], [0, np.sqrt(1-p1)]],dtype=complex)
            K1 = np.array([[0, np.sqrt(p1)], [0, 0]],dtype=complex)
            rho = self.apply_single_qubit_operator(rho, K0, q) + \
                  self.apply_single_qubit_operator(rho, K1, q)

            inv_Tphi = max(0,(1/t2_time) - (1/(2*t1_time)))
            if inv_Tphi > 0:
                Tphi = 1/inv_Tphi
                p2 = 1 - np.exp(-delta_t/Tphi)
                K0 = np.sqrt(1-p2) * np.eye(2)
                K1 = np.sqrt(p2) * np.array([[1, 0], [0, -1]],dtype=complex)
                rho = self.apply_single_qubit_operator(rho, K0, q) + \
                      self.apply_single_qubit_operator(rho, K1, q)
        return rho

    def simulate_circuit(self, shots):
        dim = 2**self.num_qubits
        rho = np.zeros((dim, dim), dtype=complex)
        rho[0, 0] = 1.0

        for gate_index, gate in enumerate(self.circuit.gates,1):
            if self.apply_decoherence == True:
                gate_delay = self.circuit.gate_info[gate.name]["Delay"]
                idle_qubits = [q for q in range(self.num_qubits) if q not in gate.qubits + self.measured_qubits]
                rho = self.apply_delay_decoherence(rho, idle_qubits, gate_delay)

            if gate.name in self.single_qubit_matrices:
                rho = self.apply_single_qubit_gate_with_bitflip(rho, gate.name, gate.qubits[0])
            elif gate.name in self.two_qubit_matrices:
                rho = self.apply_two_qubit_gate_with_bitflip(rho, gate.name, gate.qubits)
            else:
                raise ValueError("Unknown gate: "+gate.name)

            if gate.name == "measure":
                self.measured_qubits.append(gate.qubits[0])

            if gate_index % 1000 == 0:
                print(f"Step {gate_index} / {len(self.circuit.gates)} done.")

        return self.simulate_measurements(rho, shots)

    def simulate_measurements(self, rho, shots):
        probs = np.real(np.diag(rho))
        probs = np.clip(probs,0,None)
        probs /= np.sum(probs)

        states = np.arange(2**self.num_qubits)
        outcomes = np.random.choice(states, size=shots, p=probs)

        counts = {}
        for o in outcomes:
            bstr = format(o,f'0{self.num_qubits}b')
            counts[bstr] = counts.get(bstr,0) + 1

        return self.remap_measurements(counts)

    def remap_measurements(self, counts):
        new_counts = {}
        for bitstring,c in counts.items():
            bits = list(bitstring)
            new_bits = ['0']*self.num_qubits
            for logical_idx, physical_idx in self.circuit.logical_to_physical_mapping.items():
                new_bits[logical_idx] = bits[physical_idx]
            new_bitstring = ''.join(new_bits)
            rev = new_bitstring[::-1]
            new_counts[rev] = new_counts.get(rev, 0) + c

        new_counts = dict(sorted(new_counts.items(), key=lambda item:int(item[0],2)))
        return new_counts
