class CircuitGate:
    def __init__(self, name, qubits):
        self.name = name
        self.qubits = qubits

    def get_properties(self):
        return "Gate: " + self.name + " - Qubits: " + str(self.qubits)

class CircuitRepresentation:
    def __init__(self, num_qubits, device):
        self.num_qubits = num_qubits
        self.logical_to_physical_mapping = device.logical_to_physical_mapping
        self.gates = []
        self.gate_info = {g[0]: {"Error rate": g[1]/100, "Delay": g[2]} for g in device.gates}
        self.t1_times = device.t1_times
        self.t2_times = device.t2_times
        

    def add_gate(self, gate):
        self.gates.append(gate)

    def print_circuit(self):
        print("Circuit details:")
        print("    Number of qubits: " + str(self.num_qubits))
        print("    Circuit gates:")
        for gate in self.gates:
            print("        " + gate.get_properties())