import importlib.util
from qiskit import QuantumCircuit
from circuitDetails import CircuitRepresentation

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

def get_circuit_data(quantum_circuit):
    circuit_representation = CircuitRepresentation(quantum_circuit.num_qubits)

    print(quantum_circuit.data)

    return circuit_representation
