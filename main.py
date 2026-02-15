from deviceModel import VirtualNISQDevice
import circuitParser as parser

nr_qubits = 8
gates = [
    ("x", 0.2, 50),
    ("h", 0.1, 50),
    ("s", 0.05, 50),
    ("t", 0.05, 50),
    ("cx", 2, 300),
    ("swap", 0.2, 200),
    ("measure", 0.1, 100)
]
edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]

device = VirtualNISQDevice(nr_qubits, gates, edges)
device.print_properties()

qc = parser.load_circuit_from_file("idealCircuit.py")
new_qc = device.transpile_circuit(qc)

circuit_representation = parser.get_circuit_data(new_qc)
circuit_representation.print_circuit()