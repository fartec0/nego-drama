#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Genesis States module for reliable quantum state initialization.
Provides a catalog of well-defined initial quantum states with verification.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Callable
import logging

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
except ImportError:
    logging.warning("Qiskit not installed. Limited genesis state functionality available.")

class GenesisState:
    """Base class for genesis states with verification."""
    
    def __init__(self, name: str, num_qubits: int, description: str = ""):
        """Initialize a genesis state.
        
        Args:
            name: Name identifier for this genesis state
            num_qubits: Number of qubits this state requires
            description: Human-readable description of this state
        """
        self.name = name
        self.num_qubits = num_qubits
        self.description = description
        self.logger = logging.getLogger(__name__)
        
    def prepare_circuit(self) -> Optional['QuantumCircuit']:
        """Get a circuit that prepares this genesis state.
        
        Returns:
            QuantumCircuit that prepares this state when executed
        """
        raise NotImplementedError("Subclasses must implement prepare_circuit()")
        
    def get_statevector(self) -> np.ndarray:
        """Get the statevector representation of this genesis state.
        
        Returns:
            Array representing the state vector
        """
        raise NotImplementedError("Subclasses must implement get_statevector()")
        
    def verify(self, measured_state: np.ndarray, tolerance: float = 1e-6) -> Tuple[bool, float]:
        """Verify if a measured state matches this genesis state.
        
        Args:
            measured_state: Statevector or density matrix to verify
            tolerance: Numerical tolerance for verification
            
        Returns:
            Tuple of (is_valid, fidelity)
        """
        try:
            # Get the ideal state
            ideal_state = self.get_statevector()
            
            # Calculate fidelity
            fidelity = self._calculate_fidelity(ideal_state, measured_state)
            
            # Check if fidelity exceeds threshold
            is_valid = fidelity >= (1.0 - tolerance)
            
            return is_valid, fidelity
            
        except Exception as e:
            self.logger.error(f"Error verifying state: {str(e)}")
            return False, 0.0
            
    def _calculate_fidelity(self, state1: np.ndarray, state2: np.ndarray) -> float:
        """Calculate fidelity between two quantum states.
        
        Args:
            state1: First quantum state
            state2: Second quantum state
            
        Returns:
            Fidelity value between 0 and 1
        """
        # Ensure states are normalized
        state1 = state1 / np.linalg.norm(state1)
        state2 = state2 / np.linalg.norm(state2)
        
        # Calculate the inner product
        inner_product = np.abs(np.vdot(state1, state2))
        
        # Return the squared absolute value
        return inner_product ** 2
    
    def __str__(self) -> str:
        """Get string representation of this genesis state."""
        return f"{self.name} ({self.num_qubits} qubits): {self.description}"


class ComputationalBasisState(GenesisState):
    """A computational basis state |b⟩ for b in {0,1}^n."""
    
    def __init__(self, bit_string: str):
        """Initialize a computational basis state.
        
        Args:
            bit_string: Bit string representing the basis state (e.g., "01101")
        """
        self.bit_string = bit_string
        self.basis_index = int(bit_string, 2)
        num_qubits = len(bit_string)
        name = f"|{bit_string}⟩"
        description = f"Computational basis state {name}"
        
        super().__init__(name, num_qubits, description)
        
    def prepare_circuit(self) -> Optional['QuantumCircuit']:
        """Create a circuit that prepares this computational basis state.
        
        Returns:
            QuantumCircuit that prepares this state
        """
        try:
            # Create a circuit with the appropriate number of qubits
            circuit = QuantumCircuit(self.num_qubits)
            
            # Apply X gates for 1-bits
            for i, bit in enumerate(reversed(self.bit_string)):
                if bit == '1':
                    circuit.x(i)
                    
            return circuit
            
        except NameError:
            self.logger.warning("Qiskit not available, returning None")
            return None
            
    def get_statevector(self) -> np.ndarray:
        """Get the statevector for this computational basis state.
        
        Returns:
            State vector representing this basis state
        """
        # Create a zero vector of appropriate size
        state = np.zeros(2**self.num_qubits, dtype=complex)
        
        # Set the appropriate element to 1
        state[self.basis_index] = 1.0
        
        return state


class UniformSuperpositionState(GenesisState):
    """Uniform superposition state (|0⟩ + |1⟩ + ... + |2^n-1⟩)/sqrt(2^n)."""
    
    def __init__(self, num_qubits: int):
        """Initialize a uniform superposition state.
        
        Args:
            num_qubits: Number of qubits
        """
        name = "Uniform Superposition"
        description = f"Equal superposition of all {2**num_qubits} basis states"
        
        super().__init__(name, num_qubits, description)
        
    def prepare_circuit(self) -> Optional['QuantumCircuit']:
        """Create a circuit that prepares a uniform superposition.
        
        Returns:
            QuantumCircuit that prepares this state
        """
        try:
            # Create a circuit with the appropriate number of qubits
            circuit = QuantumCircuit(self.num_qubits)
            
            # Apply Hadamard gates to all qubits
            for i in range(self.num_qubits):
                circuit.h(i)
                
            return circuit
            
        except NameError:
            self.logger.warning("Qiskit not available, returning None")
            return None
            
    def get_statevector(self) -> np.ndarray:
        """Get the statevector for the uniform superposition state.
        
        Returns:
            State vector representing uniform superposition
        """
        # Create a vector with equal amplitudes
        dim = 2**self.num_qubits
        amplitude = 1.0 / np.sqrt(dim)
        
        return np.ones(dim, dtype=complex) * amplitude


class BellState(GenesisState):
    """Bell state (maximally entangled two-qubit state)."""
    
    def __init__(self, bell_type: int = 0):
        """Initialize a Bell state.
        
        Args:
            bell_type: Type of Bell state (0-3)
                0: (|00⟩ + |11⟩)/sqrt(2) (Φ⁺)
                1: (|00⟩ - |11⟩)/sqrt(2) (Φ⁻)
                2: (|01⟩ + |10⟩)/sqrt(2) (Ψ⁺)
                3: (|01⟩ - |10⟩)/sqrt(2) (Ψ⁻)
        """
        self.bell_type = bell_type % 4
        
        # Define the four Bell states
        bell_names = ["Φ⁺", "Φ⁻", "Ψ⁺", "Ψ⁻"]
        bell_desc = [
            "(|00⟩ + |11⟩)/sqrt(2)",
            "(|00⟩ - |11⟩)/sqrt(2)",
            "(|01⟩ + |10⟩)/sqrt(2)",
            "(|01⟩ - |10⟩)/sqrt(2)"
        ]
        
        name = f"Bell state {bell_names[self.bell_type]}"
        description = f"Maximally entangled two-qubit state {bell_desc[self.bell_type]}"
        
        super().__init__(name, 2, description)
        
    def prepare_circuit(self) -> Optional['QuantumCircuit']:
        """Create a circuit that prepares this Bell state.
        
        Returns:
            QuantumCircuit that prepares this state
        """
        try:
            # Create a two-qubit circuit
            circuit = QuantumCircuit(2)
            
            # Base Bell state preparation
            circuit.h(0)
            circuit.cx(0, 1)
            
            # Apply additional gates based on the Bell state type
            if self.bell_type == 1:  # Φ⁻
                circuit.z(1)
            elif self.bell_type == 2:  # Ψ⁺
                circuit.x(1)
            elif self.bell_type == 3:  # Ψ⁻
                circuit.x(1)
                circuit.z(1)
                
            return circuit
            
        except NameError:
            self.logger.warning("Qiskit not available, returning None")
            return None
            
    def get_statevector(self) -> np.ndarray:
        """Get the statevector for this Bell state.
        
        Returns:
            State vector representing this Bell state
        """
        # Create the Bell state vectors
        if self.bell_type == 0:  # Φ⁺
            state = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        elif self.bell_type == 1:  # Φ⁻
            state = np.array([1, 0, 0, -1], dtype=complex) / np.sqrt(2)
        elif self.bell_type == 2:  # Ψ⁺
            state = np.array([0, 1, 1, 0], dtype=complex) / np.sqrt(2)
        else:  # Ψ⁻
            state = np.array([0, 1, -1, 0], dtype=complex) / np.sqrt(2)
            
        return state


class GHZState(GenesisState):
    """Greenberger-Horne-Zeilinger (GHZ) state for multi-qubit entanglement."""
    
    def __init__(self, num_qubits: int):
        """Initialize a GHZ state.
        
        Args:
            num_qubits: Number of qubits (must be >= 3)
        """
        if num_qubits < 3:
            raise ValueError("GHZ state requires at least 3 qubits")
            
        name = f"GHZ-{num_qubits}"
        description = f"{num_qubits}-qubit GHZ state (|{'0'*num_qubits}⟩ + |{'1'*num_qubits}⟩)/sqrt(2)"
        
        super().__init__(name, num_qubits, description)
        
    def prepare_circuit(self) -> Optional['QuantumCircuit']:
        """Create a circuit that prepares a GHZ state.
        
        Returns:
            QuantumCircuit that prepares this state
        """
        try:
            # Create a circuit with the appropriate number of qubits
            circuit = QuantumCircuit(self.num_qubits)
            
            # Apply Hadamard to the first qubit
            circuit.h(0)
            
            # Apply CNOT gates to entangle all qubits
            for i in range(self.num_qubits - 1):
                circuit.cx(i, i+1)
                
            return circuit
            
        except NameError:
            self.logger.warning("Qiskit not available, returning None")
            return None
            
    def get_statevector(self) -> np.ndarray:
        """Get the statevector for the GHZ state.
        
        Returns:
            State vector representing the GHZ state
        """
        # Create a zero vector of appropriate size
        state = np.zeros(2**self.num_qubits, dtype=complex)
        
        # Set the first and last elements to 1/sqrt(2)
        state[0] = 1.0 / np.sqrt(2)
        state[-1] = 1.0 / np.sqrt(2)
        
        return state


class WState(GenesisState):
    """W-state for multi-qubit entanglement."""
    
    def __init__(self, num_qubits: int):
        """Initialize a W-state.
        
        Args:
            num_qubits: Number of qubits (must be >= 3)
        """
        if num_qubits < 3:
            raise ValueError("W-state requires at least 3 qubits")
            
        name = f"W-{num_qubits}"
        description = f"{num_qubits}-qubit W-state (|100...0⟩ + |010...0⟩ + ... + |000...1⟩)/sqrt({num_qubits})"
        
        super().__init__(name, num_qubits, description)
        
    def prepare_circuit(self) -> Optional['QuantumCircuit']:
        """Create a circuit that prepares a W-state.
        
        Note: Exact preparation of W-states requires complex circuits.
        This is a simplified version that uses rotations.
        
        Returns:
            QuantumCircuit that prepares this state
        """
        try:
            # Create a circuit with the appropriate number of qubits
            circuit = QuantumCircuit(self.num_qubits)
            
            # Prepare |1⟩ in the first qubit
            circuit.x(0)
            
            # Use rotations to distribute the excitation
            for i in range(self.num_qubits - 1):
                # Calculate the rotation angle
                remaining = self.num_qubits - i
                theta = 2 * np.arcsin(1.0 / np.sqrt(remaining))
                
                # Apply controlled rotation
                circuit.ry(theta, i+1)
                circuit.cx(i, i+1)
                circuit.ry(-theta, i+1)
                circuit.cx(i, i+1)
                
            return circuit
            
        except NameError:
            self.logger.warning("Qiskit not available, returning None")
            return None
            
    def get_statevector(self) -> np.ndarray:
        """Get the statevector for the W-state.
        
        Returns:
            State vector representing the W-state
        """
        # Create a zero vector of appropriate size
        state = np.zeros(2**self.num_qubits, dtype=complex)
        
        # Set the appropriate elements to 1/sqrt(n)
        amplitude = 1.0 / np.sqrt(self.num_qubits)
        
        for i in range(self.num_qubits):
            # Calculate the index with the i-th bit set to 1
            idx = 2**(self.num_qubits - i - 1)
            state[idx] = amplitude
            
        return state


class GenesisCatalog:
    """Catalog of well-defined genesis states with reliable initialization."""
    
    def __init__(self):
        """Initialize the genesis state catalog."""
        self.states = {}
        self.logger = logging.getLogger(__name__)
        
    def register_state(self, state: GenesisState) -> None:
        """Register a genesis state in the catalog.
        
        Args:
            state: Genesis state to register
        """
        key = f"{state.name}_{state.num_qubits}"
        self.states[key] = state
        self.logger.info(f"Registered genesis state: {state}")
        
    def get_state(self, name: str, num_qubits: int) -> Optional[GenesisState]:
        """Get a genesis state from the catalog.
        
        Args:
            name: Name of the genesis state
            num_qubits: Number of qubits
            
        Returns:
            Genesis state object, or None if not found
        """
        key = f"{name}_{num_qubits}"
        return self.states.get(key)
        
    def list_states(self) -> List[Dict[str, Any]]:
        """List all available genesis states.
        
        Returns:
            List of state information dictionaries
        """
        return [
            {
                "name": state.name,
                "num_qubits": state.num_qubits,
                "description": state.description
            }
            for state in self.states.values()
        ]
        
    def create_standard_catalog(self) -> None:
        """Create a catalog with standard genesis states."""
        # Register computational basis states for 1-3 qubits
        for n in range(1, 4):
            for i in range(2**n):
                bit_string = format(i, f'0{n}b')
                self.register_state(ComputationalBasisState(bit_string))
        
        # Register uniform superposition states for 1-5 qubits
        for n in range(1, 6):
            self.register_state(UniformSuperpositionState(n))
        
        # Register all four Bell states
        for i in range(4):
            self.register_state(BellState(i))
        
        # Register GHZ states for 3-5 qubits
        for n in range(3, 6):
            self.register_state(GHZState(n))
        
        # Register W-states for 3-5 qubits
        for n in range(3, 6):
            self.register_state(WState(n))
            
        self.logger.info(f"Created standard catalog with {len(self.states)} genesis states")