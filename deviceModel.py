import networkx as nx
from qiskit import transpile

class VirtualNISQDevice:
    def __init__(self, num_qubits, gates_spec, edges):
        self.num_qubits = num_qubits
        self.gates = gates_spec
        self.coupling_map = nx.Graph()
        self.coupling_map.add_edges_from(edges)
    
    def print_properties(self):
        print("The properties for this device are:")
        print("    Number of qubits: " + str(self.num_qubits))
        
        print("    Available gates:")
        for gate in self.gates:
            print("        Gate " + gate[0] + " - Error rate: " + str(gate[1]) + "% - Delay: " + str(gate[2]) + "ns")
        
        print("    Coupling Map:")
        for node in self.coupling_map.nodes():
            neighbors = list(self.coupling_map.neighbors(node))
            print("        Q" + str(node) + " connected to: " + str(neighbors))
    
    def transpile_circuit(self, quantum_circuit):
        if quantum_circuit.num_qubits > self.num_qubits:
            raise ValueError("Circuit too large for device")

        gate_names = [gate[0] for gate in self.gates]

        new_quantum_circuit = transpile(
            quantum_circuit,
            basis_gates=gate_names
        )

        return new_quantum_circuit