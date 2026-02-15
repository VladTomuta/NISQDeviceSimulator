from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

qr = QuantumRegister(2)
cr = ClassicalRegister(2)

qc = QuantumCircuit(qr, cr)

qc.h(0)
qc.cx(0, 1)
qc.cz(0, 1)
qc.x(1)
qc.swap(0, 1)

qc.measure(qr, cr)