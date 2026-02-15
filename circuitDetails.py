class CircuitGate:
    def __init__(self, name, qubits, params=None):
        self.name = name
        self.qubits = qubits
        self.params = params or []

    def get_properties(self):
        return "Gate: " + self.name + " - Qubits: " + str(self.qubits) + " - Parameters: " + str(self.params)

class CircuitRepresentation:
    def __init__(self, num_qubits):
        self.num_qubits = num_qubits
        self.gates = []

    def add_gate(self, gate):
        self.gates.append(gate)

    def print_circuit(self):
        print("Circuit details:")
        print("    Number of qubits: " + str(self.num_qubits))
        print("    Circuit gates:")
        for gate in self.gates:
            print("        " + gate.get_properties())