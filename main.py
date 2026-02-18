from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

from deviceModel import VirtualNISQDevice
from deviceSimulator import DeviceSimulator
import circuitParser as parser

nr_qubits = 5
gates = [
    ("x", 0.00015, 50),
    ("h", 0.0002, 50),
    ("s", 0.000008, 50),
    ("t", 0.000008, 50),
    ("cx", 0.0003, 300),
    ("swap", 0.00004, 200),
    ("measure", 0.0002, 100)
]
gates_half_error_rate = [
    ("x", 0.000075, 50),
    ("h", 0.0001, 50),
    ("s", 0.000004, 50),
    ("t", 0.000004, 50),
    ("cx", 0.00015, 300),
    ("swap", 0.00002, 200),
    ("measure", 0.0001, 100)
]
gates_double_error_rate = [
    ("x", 0.0003, 50),
    ("h", 0.0004, 50),
    ("s", 0.000016, 50),
    ("t", 0.000016, 50),
    ("cx", 0.0006, 300),
    ("swap", 0.00008, 200),
    ("measure", 0.0004, 100)
]

edges = [(0, 1), (0, 2), (0, 3), (0, 4)]

t1_times = [5e8, 1e9, 2.5e8, 7.5e9, 1.5e9]
t2_times = [4e8, 9e8, 2e8, 6e8, 1.2e9]
t1_times_increased = [5e9, 1e10, 2.5e9, 7.5e10, 1.5e9]
t1_times_decreased = [5e7, 1e8, 2.5e7, 7.5e8, 1.5e8]
t2_times_increased = [4e9, 9e9, 2e9, 6e9, 1.2e10]
t2_times_decreased = [4e7, 9e7, 2e7, 6e7, 1.2e8]

device = VirtualNISQDevice(nr_qubits, gates, edges, t1_times, t2_times)
device.print_properties()

print("Load circuit from file..")

qc = parser.load_circuit_from_file("idealCircuitQPE.py")
new_qc = device.transpile_circuit(qc)

print("Start parsing the circuit..")

circuit_representation = parser.get_circuit_data(new_qc, device)

print("Running simulation on ideal circuit..")

sim = AerSimulator()
result = sim.run(new_qc, shots=10000).result()
counts = result.get_counts()

simulator = DeviceSimulator(circuit_representation, True, True)

real_counts = simulator.simulate_circuit(shots=10000)

normalized_counts = {}

num_ancila_qubits = 2

for bitstring, value in real_counts.items():
    new_key = bitstring[num_ancila_qubits:] if num_ancila_qubits > 0 else bitstring
    normalized_counts[new_key] = normalized_counts.get(new_key, 0) + value

sorted_counts = dict(sorted(counts.items()))

print("Ideal circuit counts:")
print(sorted_counts)

print("Real circuit counts:")
print(real_counts)

print("Real circuit without ancila qubits counts:")
print(normalized_counts)

bars = plt.bar(sorted_counts.keys(), sorted_counts.values())
plt.bar_label(bars, padding=3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

bars = plt.bar(real_counts.keys(), real_counts.values())
plt.bar_label(bars, padding=3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

bars = plt.bar(normalized_counts.keys(), normalized_counts.values())
plt.bar_label(bars, padding=3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()