import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator

phi = 0.3
t = 3
n_target = 2

qc = QuantumCircuit(t + n_target, t)

for i in range(n_target):
    qc.x(t + i)

for i in range(t):
    qc.h(i)

for j in range(t):
    angle = 2 * np.pi * phi * (2**j)
    for target_qubit in range(n_target):
        qc.crz(angle, j, t + target_qubit)

qc.append(QFT(t, inverse=True, do_swaps=True).decompose(), range(t))

for i in range(n_target):
    qc.x(t + i)

qc.measure(range(t), range(t))
