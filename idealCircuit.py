from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

qr = QuantumRegister(3)
cr = ClassicalRegister(3)

qc = QuantumCircuit(qr, cr)

qc.h(0)
qc.cx(0, 1)
qc.cz(0, 1)
qc.x(1)
qc.swap(0, 1)

qc.cx(1, 2)

qc.measure(qr, cr)