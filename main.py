from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

from deviceModel import VirtualNISQDevice
from deviceSimulator import DeviceSimulator
import circuitParser as parser

nr_qubits = 5
gates = [
    ("x", 0.00008, 50),
    ("h", 0.0001, 50),
    ("s", 0.000005, 50),
    ("t", 0.000005, 50),
    ("cx", 0.0003, 300),
    ("swap", 0.00004, 200),
    ("measure", 0.0002, 100)
]
edges = [(0, 1), (0, 2), (0, 3), (0, 4)]
t1_times = [5e8, 1e9, 2.5e8, 7.5e9, 1.5e9]
t2_times = [4e8, 9e8, 2e8, 6e8, 1.2e9]

device = VirtualNISQDevice(nr_qubits, gates, edges, t1_times, t2_times)
device.print_properties()

print("Load circuit from file..")

qc = parser.load_circuit_from_file("idealCircuitQPE.py")
#qc = parser.load_circuit_from_file("idealCircuitGrover.py")
new_qc = device.transpile_circuit(qc)

print("Start parsing the circuit..")

print(new_qc.num_qubits)

circuit_representation = parser.get_circuit_data(new_qc, device)

print(circuit_representation.num_qubits)

sim = AerSimulator()

print("Running simulation on ideal circuit..")

result = sim.run(new_qc, shots=10000).result()
counts = result.get_counts()
print(counts)

simulator = DeviceSimulator(circuit_representation, True, True)

print(len(circuit_representation.gates))

real_counts = simulator.simulate_circuit(shots=10000)

print(real_counts)

normalized_counts = {}

num_ancila_qubits = 2

for bitstring, value in real_counts.items():
    new_key = bitstring[num_ancila_qubits:] if num_ancila_qubits > 0 else bitstring
    normalized_counts[new_key] = normalized_counts.get(new_key, 0) + value

print(normalized_counts)

sorted_counts = dict(sorted(counts.items()))

plt.bar(sorted_counts.keys(), sorted_counts.values())
plt.show()

plt.bar(real_counts.keys(), real_counts.values())
plt.show()

plt.bar(normalized_counts.keys(), normalized_counts.values())
plt.show()