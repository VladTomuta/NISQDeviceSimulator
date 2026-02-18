import importlib.util
from qiskit import QuantumCircuit
from circuitDetails import CircuitRepresentation, CircuitGate

def load_circuit_from_file(filename):
    spec = importlib.util.spec_from_file_location("user_module", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    circuits = []

    for obj in vars(module).values():
        if isinstance(obj, QuantumCircuit):
            circuits.append(obj)

    if len(circuits) == 0:
        raise ValueError("No QuantumCircuit found in the input file.")

    if len(circuits) > 1:
        raise ValueError("Multiple QuantumCircuit objects found. Please define only one.")

    return circuits[0]

def get_circuit_data(quantum_circuit, device):
    circuit_representation = CircuitRepresentation(quantum_circuit.num_qubits, device)
    print(circuit_representation.num_qubits)

    for instruction, qargs, cargs in quantum_circuit.data:
        name = instruction.name
        qubits = [quantum_circuit.qubits.index(q) for q in qargs]

        gate = CircuitGate(name, qubits)
        circuit_representation.add_gate(gate)

    return circuit_representation
