#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
Implementation of Grover's search algorithm for quantum search.
"""

import numpy as np
from typing import List, Optional, Tuple, Dict, Any, Union, Callable
import logging
from functools import lru_cache

try:
    from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
    from qiskit.quantum_info import Statevector
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    logging.warning("Qiskit not available. Using numpy-based simulation instead.")


class GroversAlgorithm:
    """Implementation of Grover's quantum search algorithm."""
    
    def __init__(self, num_qubits: int, oracle_function: Optional[Callable] = None):
        """Initialize the Grover's algorithm implementation.
        
        Args:
            num_qubits: Number of qubits to use
            oracle_function: Function that returns True for marked items
        """
        self.num_qubits = num_qubits
        self.oracle_function = oracle_function
        self.logger = logging.getLogger(__name__)
        
        # Calculate optimal number of iterations
        self.optimal_iterations = self._calculate_optimal_iterations()
        
        # Check if Qiskit is available
        self.using_qiskit = QISKIT_AVAILABLE
        
    def _calculate_optimal_iterations(self) -> int:
        """Calculate the optimal number of Grover iterations.
        
        Returns:
            Optimal number of iterations
        """
        # For a random search in a database of N items, Grover's algorithm 
        # requires approximately π/4 * sqrt(N) iterations
        N = 2**self.num_qubits
        return int(np.round(np.pi/4 * np.sqrt(N)))
        
    def create_oracle_circuit(self, marked_states: List[str]) -> 'QuantumCircuit':
        """Create a quantum circuit implementing the oracle function.
        
        Args:
            marked_states: List of binary strings representing marked states
            
        Returns:
            Quantum circuit implementing the oracle
        """
        if not self.using_qiskit:
            raise ImportError("Qiskit is required for circuit creation")
            
        # Create a quantum circuit with num_qubits
        qr = QuantumRegister(self.num_qubits, 'q')
        oracle_circuit = QuantumCircuit(qr, name="oracle")
        
        # Convert marked states to integers
        marked_indices = [int(state, 2) for state in marked_states]
        
        # For each marked state, create a multi-controlled Z gate
        for idx in marked_indices:
            # Convert index to binary string with leading zeros
            binary = format(idx, f'0{self.num_qubits}b')
            
            # Apply X gates where binary digits are 0
            for qubit, bit in enumerate(reversed(binary)):
                if bit == '0':
                    oracle_circuit.x(qr[qubit])
            
            # Apply multi-controlled Z gate
            if self.num_qubits == 1:
                oracle_circuit.z(qr[0])
            elif self.num_qubits == 2:
                oracle_circuit.cz(qr[0], qr[1])
            else:
                # For more than 2 qubits, use multi-controlled Z implementation
                # Apply H to the last qubit
                oracle_circuit.h(qr[self.num_qubits-1])
                
                # Apply multi-controlled X gate
                if self.num_qubits == 3:
                    oracle_circuit.ccx(qr[0], qr[1], qr[2])
                else:
                    # For more qubits, decompose into multiple Toffoli gates if needed
                    # This is a simplified implementation; real-world would use more optimized approaches
                    if self.num_qubits <= 5:  # Use direct CCX gates for up to 5 qubits
                        control_qubits = list(range(self.num_qubits-1))
                        target_qubit = self.num_qubits-1
                        oracle_circuit.mct(
                            control_qubits=[qr[i] for i in control_qubits],
                            target_qubit=qr[target_qubit]
                        )
                    else:
                        # For more qubits, a more complex implementation would be needed
                        # This is a placeholder for demonstration
                        self.logger.warning("Using approximation for large multi-controlled Z gate")
                        # Simplified approach: break into multiple Toffoli gates
                        ancilla = QuantumRegister(self.num_qubits-3, 'ancilla')
                        oracle_circuit.add_register(ancilla)
                        
                        # First Toffoli
                        oracle_circuit.ccx(qr[0], qr[1], ancilla[0])
                        
                        # Middle Toffolis
                        for i in range(self.num_qubits-5):
                            oracle_circuit.ccx(ancilla[i], qr[i+2], ancilla[i+1])
                            
                        # Last Toffoli
                        oracle_circuit.ccx(ancilla[self.num_qubits-5], qr[self.num_qubits-3], qr[self.num_qubits-1])
                        
                        # Uncompute ancillas
                        for i in range(self.num_qubits-5, 0, -1):
                            oracle_circuit.ccx(ancilla[i-1], qr[i+1], ancilla[i])
                            
                        # Final uncomputation
                        oracle_circuit.ccx(qr[0], qr[1], ancilla[0])
                
                # Apply H to the last qubit again
                oracle_circuit.h(qr[self.num_qubits-1])
            
            # Apply X gates again to restore the state
            for qubit, bit in enumerate(reversed(binary)):
                if bit == '0':
                    oracle_circuit.x(qr[qubit])
        
        return oracle_circuit
        
    def create_diffusion_circuit(self) -> 'QuantumCircuit':
        """Create a quantum circuit implementing the diffusion operator.
        
        Returns:
            Quantum circuit implementing the diffusion operator
        """
        if not self.using_qiskit:
            raise ImportError("Qiskit is required for circuit creation")
            
        # Create a quantum circuit with num_qubits
        qr = QuantumRegister(self.num_qubits, 'q')
        diffusion_circuit = QuantumCircuit(qr, name="diffusion")
        
        # Apply H gates to all qubits
        for qubit in range(self.num_qubits):
            diffusion_circuit.h(qr[qubit])
            
        # Apply X gates to all qubits
        for qubit in range(self.num_qubits):
            diffusion_circuit.x(qr[qubit])
            
        # Apply multi-controlled Z gate (2|0⟩⟨0| - I)
        # First apply H to the last qubit
        diffusion_circuit.h(qr[self.num_qubits-1])
        
        # Apply multi-controlled X gate
        if self.num_qubits == 1:
            diffusion_circuit.x(qr[0])
        elif self.num_qubits == 2:
            diffusion_circuit.cx(qr[0], qr[1])
        elif self.num_qubits == 3:
            diffusion_circuit.ccx(qr[0], qr[1], qr[2])
        else:
            # For more qubits, use multi-controlled X implementation
            if self.num_qubits <= 5:  # Use direct MCT for up to 5 qubits
                control_qubits = list(range(self.num_qubits-1))
                target_qubit = self.num_qubits-1
                diffusion_circuit.mct(
                    control_qubits=[qr[i] for i in control_qubits],
                    target_qubit=qr[target_qubit]
                )
            else:
                # For more qubits, a more complex implementation would be needed
                # This is a placeholder for demonstration
                self.logger.warning("Using approximation for large multi-controlled Z gate")
                # Simplified approach: break into multiple Toffoli gates
                ancilla = QuantumRegister(self.num_qubits-3, 'ancilla')
                diffusion_circuit.add_register(ancilla)
                
                # First Toffoli
                diffusion_circuit.ccx(qr[0], qr[1], ancilla[0])
                
                # Middle Toffolis
                for i in range(self.num_qubits-5):
                    diffusion_circuit.ccx(ancilla[i], qr[i+2], ancilla[i+1])
                    
                # Last Toffoli
                diffusion_circuit.ccx(ancilla[self.num_qubits-5], qr[self.num_qubits-3], qr[self.num_qubits-1])
                
                # Uncompute ancillas
                for i in range(self.num_qubits-5, 0, -1):
                    diffusion_circuit.ccx(ancilla[i-1], qr[i+1], ancilla[i])
                    
                # Final uncomputation
                diffusion_circuit.ccx(qr[0], qr[1], ancilla[0])
        
        # Apply H to the last qubit again
        diffusion_circuit.h(qr[self.num_qubits-1])
        
        # Apply X gates to all qubits
        for qubit in range(self.num_qubits):
            diffusion_circuit.x(qr[qubit])
            
        # Apply H gates to all qubits
        for qubit in range(self.num_qubits):
            diffusion_circuit.h(qr[qubit])
            
        return diffusion_circuit
        
    def create_full_circuit(self, marked_states: List[str], iterations: Optional[int] = None) -> 'QuantumCircuit':
        """Create a full Grover's algorithm circuit.
        
        Args:
            marked_states: List of binary strings representing marked states
            iterations: Number of iterations to perform (default: optimal)
            
        Returns:
            Complete Grover's algorithm circuit
        """
        if not self.using_qiskit:
            raise ImportError("Qiskit is required for circuit creation")
            
        # Use optimal iterations if not specified
        if iterations is None:
            iterations = self.optimal_iterations
            
        # Create quantum and classical registers
        qr = QuantumRegister(self.num_qubits, 'q')
        cr = ClassicalRegister(self.num_qubits, 'c')
        
        # Create a quantum circuit
        circuit = QuantumCircuit(qr, cr, name="Grover")
        
        # Apply H gates to all qubits (initialize superposition)
        for qubit in range(self.num_qubits):
            circuit.h(qr[qubit])
            
        # Create oracle and diffusion circuits
        oracle_circuit = self.create_oracle_circuit(marked_states)
        diffusion_circuit = self.create_diffusion_circuit()
        
        # Add a barrier for clear visualization
        circuit.barrier()
        
        # Apply Grover iterations
        for _ in range(iterations):
            # Apply oracle
            circuit.append(oracle_circuit, qr)
            
            # Add a barrier for clear visualization
            circuit.barrier()
            
            # Apply diffusion operator
            circuit.append(diffusion_circuit, qr)
            
            # Add a barrier for clear visualization
            circuit.barrier()
            
        # Measure all qubits
        circuit.measure(qr, cr)
        
        return circuit
        
    def simulate_circuit(self, circuit: 'QuantumCircuit', shots: int = 1024) -> Dict[str, int]:
        """Simulate the quantum circuit and return measurement results.
        
        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots
            
        Returns:
            Dictionary of measurement results
        """
        if not self.using_qiskit:
            raise ImportError("Qiskit is required for circuit simulation")
            
        try:
            from qiskit import Aer, execute
            
            # Use the qasm_simulator
            simulator = Aer.get_backend('qasm_simulator')
            
            # Execute the circuit
            job = execute(circuit, simulator, shots=shots)
            
            # Get the result
            result = job.result()
            
            # Get the counts
            counts = result.get_counts(circuit)
            
            return counts
            
        except Exception as e:
            self.logger.error(f"Error simulating circuit: {str(e)}")
            return {}
            
    def get_statevector(self, circuit: 'QuantumCircuit') -> np.ndarray:
        """Get the statevector after running the circuit without measurement.
        
        Args:
            circuit: Quantum circuit to simulate (without measurement)
            
        Returns:
            Statevector as numpy array
        """
        if not self.using_qiskit:
            raise ImportError("Qiskit is required for statevector simulation")
            
        try:
            from qiskit import Aer, execute
            
            # Use the statevector_simulator
            simulator = Aer.get_backend('statevector_simulator')
            
            # Remove measurement operations
            circuit_no_measure = circuit.copy()
            circuit_no_measure.remove_final_measurements()
            
            # Execute the circuit
            job = execute(circuit_no_measure, simulator)
            
            # Get the result
            result = job.result()
            
            # Get the statevector
            statevector = result.get_statevector()
            
            return statevector.data
            
        except Exception as e:
            self.logger.error(f"Error getting statevector: {str(e)}")
            return np.zeros(2**self.num_qubits)
            
    def search(self, 
              marked_states: List[str], 
              iterations: Optional[int] = None, 
              shots: int = 1024) -> Dict[str, Any]:
        """Run Grover's search algorithm to find marked states.
        
        Args:
            marked_states: List of binary strings representing marked states
            iterations: Number of iterations to perform (default: optimal)
            shots: Number of measurement shots
            
        Returns:
            Dictionary containing search results
        """
        if not self.using_qiskit:
            raise ImportError("Qiskit is required for Grover's algorithm")
            
        # Create the complete circuit
        circuit = self.create_full_circuit(marked_states, iterations)
        
        # Get the statevector
        statevector = self.get_statevector(circuit)
        
        # Simulate the circuit
        counts = self.simulate_circuit(circuit, shots)
        
        # Calculate success probability
        success_count = sum(counts.get(state, 0) for state in marked_states)
        success_prob = success_count / shots if shots > 0 else 0
        
        # Return results
        return {
            'circuit': circuit,
            'statevector': statevector,
            'counts': counts,
            'success_probability': success_prob,
            'marked_states': marked_states,
            'iterations': iterations if iterations is not None else self.optimal_iterations
        }
        
    @staticmethod
    def calculate_success_probability(num_qubits: int, num_marked: int, iterations: int) -> float:
        """Calculate the theoretical success probability for Grover's algorithm.
        
        Args:
            num_qubits: Number of qubits
            num_marked: Number of marked items
            iterations: Number of Grover iterations
            
        Returns:
            Theoretical success probability
        """
        N = 2**num_qubits  # Size of the search space
        M = num_marked     # Number of marked items
        
        # Calculate the amplitude amplification
        theta = np.arcsin(np.sqrt(M/N))
        prob = np.sin((2*iterations + 1) * theta)**2
        
        return prob
        
    @staticmethod
    def estimate_required_iterations(num_qubits: int, num_marked: int, 
                                   target_prob: float = 0.99) -> int:
        """Estimate the number of iterations needed to achieve a target success probability.
        
        Args:
            num_qubits: Number of qubits
            num_marked: Number of marked items
            target_prob: Target success probability
            
        Returns:
            Estimated number of iterations
        """
        N = 2**num_qubits  # Size of the search space
        M = num_marked     # Number of marked items
        
        # Calculate optimal number of iterations
        theta = np.arcsin(np.sqrt(M/N))
        iterations = np.round((np.arcsin(np.sqrt(target_prob)) - theta) / (2*theta))
        
        return max(1, int(iterations))
        
    @staticmethod
    @lru_cache(maxsize=128)
    def optimal_iterations_for_target(num_qubits: int, num_marked: int, 
                                     target_prob: float = 0.95) -> int:
        """Calculate the optimal number of iterations for a target probability.
        
        Args:
            num_qubits: Number of qubits
            num_marked: Number of marked items
            target_prob: Target success probability
            
        Returns:
            Optimal number of iterations
        """
        N = 2**num_qubits  # Size of the search space
        M = num_marked     # Number of marked items
        
        if M >= N/2:
            # If more than half the items are marked, a single iteration is optimal
            return 1
            
        # Calculate the optimal number of iterations
        theta = np.arcsin(np.sqrt(M/N))
        
        # Find the number of iterations that maximizes the success probability
        # without exceeding the target probability
        best_iter = 0
        best_prob = 0
        
        # Try different numbers of iterations
        for i in range(1, int(np.pi/(4*theta))+2):
            prob = np.sin((2*i + 1) * theta)**2
            if best_prob < prob <= target_prob:
                best_prob = prob
                best_iter = i
                
            # If we've reached or exceeded the target, we're done
            if prob >= target_prob:
                return i
                
        # If we didn't reach the target, return the best we found
        return max(1, best_iter)