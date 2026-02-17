from qiskit_aer import AerSimulator
import numpy as np

from deviceModel import VirtualNISQDevice
from deviceSimulator import DeviceSimulator
import circuitParser as parser

#nr_qubits = 8
nr_qubits = 5
#gates = [
#    ("x", 0, 50),
#    ("h", 0, 50),
#    ("s", 0, 50),
#    ("t", 0, 50),
#    ("cx", 0, 300),
#    ("swap", 0, 200),
#    ("measure", 0, 100)
#]
gates = [
    ("x", 0.00002, 50),
    ("h", 0.00001, 50),
    ("s", 0.000005, 50),
    ("t", 0.000005, 50),
    ("cx", 0.0002, 300),
    ("swap", 0.00002, 200),
    ("measure", 0.0001, 100)
]
#edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]
edges = [(0, 1), (0, 2), (0, 3), (0, 4)]
t1_time = [0.00001, 0.00003, 0.00007, 0.00004, 0.0001]
t2_time = [0.00001, 0.00002, 0.00005, 0.00004, 0.00015]

device = VirtualNISQDevice(nr_qubits, gates, edges, t1_time, t2_time)
device.print_properties()

print("Load circuit from file..")

qc = parser.load_circuit_from_file("idealCircuitQPE.py")
#qc = parser.load_circuit_from_file("idealCircuitGrover.py")
new_qc = device.transpile_circuit(qc)

print("Start parsing the circuit..")

circuit_representation = parser.get_circuit_data(new_qc)
#circuit_representation.print_circuit()

sim = AerSimulator()

#print("Running simulation on ideal circuit..")

#result = sim.run(qc, shots=1000).result()
#counts = result.get_counts()
#print(qc)
#print(counts)

print("Running simulation on ideal circuit..")

result = sim.run(new_qc, shots=1000).result()
counts = result.get_counts()
print(counts)

simulator = DeviceSimulator(device, circuit_representation)

print(len(circuit_representation.gates))

simulator.simulate_circuit(shots=1000)