import networkx as nx

class VirtualNISQDevice:
    def __init__(self, nr_qubits, gates_spec, edges):
        self.nr_qubits = nr_qubits
        self.gates = gates_spec
        self.coupling_map = nx.Graph()
        self.coupling_map.add_edges_from(edges)
    
    def print_properties(self):
        print("The properties for this device are:")
        print("    Number of qubits: " + str(self.nr_qubits))
        
        print("    Available gates:")
        for gate in self.gates:
            print("        Gate " + gate[0] + " - Error rate: " + str(gate[1]) + "% - Delay: " + str(gate[2]) + "ns")
        
        print("    Coupling Map:")
        for node in self.coupling_map.nodes():
            neighbors = list(self.coupling_map.neighbors(node))
            print("        Q" + str(node) + " connected to: " + str(neighbors))