#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple quantum circuit simulator for the Quantum UI.
This module provides basic quantum circuit simulation functionality.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional

class QuantumSimulator:
    """A simple quantum circuit simulator."""
    
    def __init__(self, num_qubits: int):
        """Initialize the quantum simulator.
        
        Args:
            num_qubits: Number of qubits in the system
        """
        self.num_qubits = num_qubits
        self.num_states = 2**num_qubits
        
        # Initialize state vector to |0>
        self.state_vector = np.zeros(self.num_states)
        self.state_vector[0] = 1.0
        
        # Define common gates
        self._define_gates()
        
    def _define_gates(self) -> None:
        """Define common quantum gates."""
        # Single-qubit gates
        self.gates = {
            "I": np.array([[1, 0], [0, 1]], dtype=complex),
            "X": np.array([[0, 1], [1, 0]], dtype=complex),
            "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
            "Z": np.array([[1, 0], [0, -1]], dtype=complex),
            "H": np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),
            "S": np.array([[1, 0], [0, 1j]], dtype=complex),
            "T": np.array([[1, 0], [0, np.exp(1j * np.pi/4)]], dtype=complex)
        }
        
    def apply_gate(self, gate_name: str, target_qubit: int, 
                  control_qubit: Optional[int] = None) -> None:
        """Apply a quantum gate to the state vector.
        
        Args:
            gate_name: Name of the gate to apply
            target_qubit: Target qubit index
            control_qubit: Control qubit index (for controlled gates)
        """
        if gate_name not in self.gates and gate_name not in ["CNOT", "SWAP", "Toffoli"]:
            raise ValueError(f"Gate {gate_name} not supported")
            
        if target_qubit >= self.num_qubits or (control_qubit is not None and control_qubit >= self.num_qubits):
            raise ValueError("Qubit index out of range")
            
        # Apply single-qubit gate
        if gate_name in self.gates and control_qubit is None:
            gate = self.gates[gate_name]
            self._apply_single_qubit_gate(gate, target_qubit)
            
        # Apply CNOT gate
        elif gate_name == "CNOT" and control_qubit is not None:
            self._apply_cnot(control_qubit, target_qubit)
            
        # Apply SWAP gate
        elif gate_name == "SWAP" and control_qubit is not None:
            self._apply_swap(target_qubit, control_qubit)
            
        # Apply Toffoli gate
        elif gate_name == "Toffoli" and control_qubit is not None:
            # For simplicity, we'll assume the second control is the next qubit after the first control
            self._apply_toffoli(control_qubit, control_qubit + 1, target_qubit)
            
        else:
            raise ValueError("Invalid gate configuration")
    
    def _apply_single_qubit_gate(self, gate: np.ndarray, target_qubit: int) -> None:
        """Apply a single-qubit gate to the state vector.
        
        Args:
            gate: 2x2 gate matrix
            target_qubit: Target qubit index
        """
        # Create identity matrices for other qubits
        matrices = [np.eye(2, dtype=complex) for _ in range(self.num_qubits)]
        matrices[target_qubit] = gate
        
        # Construct the full operator using tensor products
        operator = matrices[0]
        for i in range(1, self.num_qubits):
            operator = np.kron(operator, matrices[i])
            
        # Apply the operator
        self.state_vector = operator @ self.state_vector
        
    def _apply_cnot(self, control_qubit: int, target_qubit: int) -> None:
        """Apply a CNOT gate to the state vector.
        
        Args:
            control_qubit: Control qubit index
            target_qubit: Target qubit index
        """
        # For each basis state
        new_state = np.zeros_like(self.state_vector, dtype=complex)
        
        for i in range(self.num_states):
            # Convert to binary representation
            binary = format(i, f'0{self.num_qubits}b')
            
            # Check if control qubit is 1
            if binary[control_qubit] == '1':
                # Flip target qubit
                new_binary = list(binary)
                new_binary[target_qubit] = '1' if binary[target_qubit] == '0' else '0'
                new_binary = ''.join(new_binary)
                
                # Calculate new state index
                new_idx = int(new_binary, 2)
                
                # Update state
                new_state[new_idx] = self.state_vector[i]
            else:
                # Control is 0, no change
                new_state[i] = self.state_vector[i]
                
        self.state_vector = new_state
    
    def _apply_swap(self, qubit1: int, qubit2: int) -> None:
        """Apply a SWAP gate to the state vector.
        
        Args:
            qubit1: First qubit index
            qubit2: Second qubit index
        """
        # For each basis state
        new_state = np.zeros_like(self.state_vector, dtype=complex)
        
        for i in range(self.num_states):
            # Convert to binary representation
            binary = format(i, f'0{self.num_qubits}b')
            
            # Swap the qubits
            new_binary = list(binary)
            new_binary[qubit1], new_binary[qubit2] = binary[qubit2], binary[qubit1]
            new_binary = ''.join(new_binary)
            
            # Calculate new state index
            new_idx = int(new_binary, 2)
            
            # Update state
            new_state[new_idx] = self.state_vector[i]
                
        self.state_vector = new_state
        
    def _apply_toffoli(self, control1: int, control2: int, target: int) -> None:
        """Apply a Toffoli gate to the state vector.
        
        Args:
            control1: First control qubit index
            control2: Second control qubit index
            target: Target qubit index
        """
        # For each basis state
        new_state = np.zeros_like(self.state_vector, dtype=complex)
        
        for i in range(self.num_states):
            # Convert to binary representation
            binary = format(i, f'0{self.num_qubits}b')
            
            # Check if both control qubits are 1
            if binary[control1] == '1' and binary[control2] == '1':
                # Flip target qubit
                new_binary = list(binary)
                new_binary[target] = '1' if binary[target] == '0' else '0'
                new_binary = ''.join(new_binary)
                
                # Calculate new state index
                new_idx = int(new_binary, 2)
                
                # Update state
                new_state[new_idx] = self.state_vector[i]
            else:
                # At least one control is 0, no change
                new_state[i] = self.state_vector[i]
                
        self.state_vector = new_state
    
    def reset(self) -> None:
        """Reset the state vector to |0>."""
        self.state_vector = np.zeros(self.num_states)
        self.state_vector[0] = 1.0
        
    def initialize_state(self, state: np.ndarray) -> None:
        """Initialize with a custom state vector.
        
        Args:
            state: New state vector
        """
        if len(state) != self.num_states:
            raise ValueError(f"State vector must have {self.num_states} elements")
            
        # Normalize the state
        norm = np.linalg.norm(state)
        if norm > 0:
            self.state_vector = state / norm
        else:
            raise ValueError("State vector cannot be zero")
            
    def apply_circuit(self, circuit: List[Dict[str, Any]]) -> None:
        """Apply a quantum circuit (sequence of gates).
        
        Args:
            circuit: List of gate operations
                Each operation is a dict with keys:
                - 'gate': Gate name
                - 'target': Target qubit
                - 'control': Control qubit (optional)
        """
        for operation in circuit:
            self.apply_gate(
                operation["gate"],
                operation["target"],
                operation.get("control")
            )
            
    def get_statevector(self) -> np.ndarray:
        """Get the current state vector.
        
        Returns:
            Current state vector
        """
        return self.state_vector
        
    def get_probabilities(self) -> np.ndarray:
        """Get measurement probabilities.
        
        Returns:
            Array of measurement probabilities
        """
        return np.abs(self.state_vector)**2
        
    def measure(self, num_shots: int = 1) -> Dict[str, int]:
        """Perform measurement on the quantum state.
        
        Args:
            num_shots: Number of measurement shots
            
        Returns:
            Dictionary mapping bit strings to counts
        """
        probabilities = self.get_probabilities()
        results = {}
        
        # Perform measurements
        outcomes = np.random.choice(self.num_states, size=num_shots, p=probabilities)
        
        # Count results
        for outcome in outcomes:
            bit_string = format(outcome, f'0{self.num_qubits}b')
            results[bit_string] = results.get(bit_string, 0) + 1
            
        return results