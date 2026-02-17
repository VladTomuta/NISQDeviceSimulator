from qiskit import transpile
from qiskit.transpiler import CouplingMap

class VirtualNISQDevice:
    def __init__(self, num_qubits, gates_spec, edges):
        self.num_qubits = num_qubits
        self.gates = gates_spec
        self.edges = edges
    
    def print_properties(self):
        print("The properties for this device are:")
        print("    Number of qubits: " + str(self.num_qubits))
        
        print("    Available gates:")
        for gate in self.gates:
            print("        Gate " + gate[0] + " - Error rate: " + str(gate[1]) + "% - Delay: " + str(gate[2]) + "ns")
        
        coupling_map = [[] for _ in range(self.num_qubits)]

        for q1, q2 in self.edges:
            coupling_map[q1].append(q2)
            coupling_map[q2].append(q1)
        
        print("    Coupling Map:")
        for qubit, neighbors in enumerate(coupling_map):
            neighbors_str = ", ".join(str(n) for n in sorted(neighbors))
            print("        Q" + str(qubit) + " -> " + neighbors_str)
        
    def transpile_circuit(self, quantum_circuit):
        if quantum_circuit.num_qubits > self.num_qubits:
            raise ValueError("Circuit too large for device")

        gate_names = [gate[0] for gate in self.gates]

        coupling = CouplingMap(couplinglist=self.edges)

        new_quantum_circuit = transpile(
            quantum_circuit,
            basis_gates=gate_names,
            coupling_map=coupling,
            routing_method="sabre"
        )
        """
        print("Optimized transpile")

        new_quantum_circuit = transpile(
            quantum_circuit,
            basis_gates=gate_names,
            coupling_map=coupling,
            routing_method="lookahead",          # or "lookahead" for fewer SWAPs
            optimization_level=3,            # heavy optimization
            initial_layout=quantum_circuit.qubits,
            seed_transpiler=42               # reproducible results
        )
        """

        final_indices = new_quantum_circuit.layout.final_index_layout()
        self.logical_to_physical_mapping = {i: phys_idx for i, phys_idx in enumerate(final_indices)}

        return new_quantum_circuit