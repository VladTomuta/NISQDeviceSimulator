from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import math as math

num_qubits = 3

qr = QuantumRegister(num_qubits + 1)
cr = ClassicalRegister(num_qubits + 1)

qc = QuantumCircuit(qr, cr)

print((math.pi/4 * math.sqrt(math.pow(2, num_qubits))))

qc.x(num_qubits)
for i in range(num_qubits + 1):
    qc.h(i)

for _ in range(math.floor(math.pi/4 * math.sqrt(math.pow(2, num_qubits)))):
    qc.mcx(list(range(num_qubits)), num_qubits)

    for i in range(num_qubits):
        qc.h(i)
        qc.x(i)

    qc.h(num_qubits-1)
    qc.mcx(list(range(num_qubits-1)), num_qubits-1)
    qc.h(num_qubits-1)

    for i in range(num_qubits):
        qc.x(i)
        qc.h(i)

qc.h(num_qubits)
qc.x(num_qubits)

qc.measure(range(num_qubits + 1), range(num_qubits + 1))
