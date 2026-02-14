from deviceModel import VirtualNISQDevice

nr_qubits = 8
gates = [
    ("X", 0.2, 50),
    ("H", 0.1, 50),
    ("S", 0.05, 50),
    ("T", 0.05, 50),
    ("CNOT", 2, 300)
]
edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]

device = VirtualNISQDevice(nr_qubits, gates, edges)
device.print_properties()
