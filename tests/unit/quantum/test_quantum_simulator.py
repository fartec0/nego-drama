#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
Unit tests for the quantum simulator module.
"""

import unittest
import numpy as np
from src.quantum.simulators.quantum_simulator import QuantumSimulator

class TestQuantumSimulator(unittest.TestCase):
    """Test cases for the quantum simulator."""
    
    def test_initialization(self):
        """Test simulator initialization."""
        # Create simulator with 2 qubits
        simulator = QuantumSimulator(2)
        
        # Check initial state is |00>
        state_vector = simulator.get_statevector()
        expected = np.zeros(4)
        expected[0] = 1.0
        
        np.testing.assert_array_almost_equal(state_vector, expected)
        
    def test_single_qubit_gates(self):
        """Test single-qubit gates."""
        # Create simulator with 1 qubit
        simulator = QuantumSimulator(1)
        
        # Apply X gate (NOT gate)
        simulator.apply_gate("X", 0)
        
        # Check state is |1>
        state_vector = simulator.get_statevector()
        expected = np.zeros(2)
        expected[1] = 1.0
        
        np.testing.assert_array_almost_equal(state_vector, expected)
        
        # Reset and apply H gate
        simulator.reset()
        simulator.apply_gate("H", 0)
        
        # Check state is (|0> + |1>)/sqrt(2)
        state_vector = simulator.get_statevector()
        expected = np.ones(2) / np.sqrt(2)
        
        np.testing.assert_array_almost_equal(state_vector, expected)
    
    def test_cnot_gate(self):
        """Test CNOT gate."""
        # Create simulator with 2 qubits
        simulator = QuantumSimulator(2)
        
        # Prepare |10> state (X on first qubit)
        simulator.apply_gate("X", 0)
        
        # Apply CNOT with control=0, target=1
        simulator.apply_gate("CNOT", 1, 0)
        
        # Check state is |11>
        state_vector = simulator.get_statevector()
        expected = np.zeros(4)
        expected[3] = 1.0  # |11> corresponds to index 3
        
        np.testing.assert_array_almost_equal(state_vector, expected)
    
    def test_bell_state(self):
        """Test creating a Bell state."""
        # Create simulator with 2 qubits
        simulator = QuantumSimulator(2)
        
        # Apply H to first qubit
        simulator.apply_gate("H", 0)
        
        # Apply CNOT with control=0, target=1
        simulator.apply_gate("CNOT", 1, 0)
        
        # Check state is (|00> + |11>)/sqrt(2)
        state_vector = simulator.get_statevector()
        expected = np.zeros(4)
        expected[0] = 1.0 / np.sqrt(2)  # |00>
        expected[3] = 1.0 / np.sqrt(2)  # |11>
        
        np.testing.assert_array_almost_equal(state_vector, expected)
    
    def test_measurement(self):
        """Test measurement statistics."""
        # Create simulator with a single qubit
        simulator = QuantumSimulator(1)
        
        # Apply H gate to create superposition
        simulator.apply_gate("H", 0)
        
        # Perform many measurements
        num_shots = 1000
        results = simulator.measure(num_shots)
        
        # Check we have results for both |0> and |1>
        self.assertIn("0", results)
        self.assertIn("1", results)
        
        # Check counts are roughly equal (within statistical bounds)
        self.assertGreater(results["0"], num_shots * 0.4)
        self.assertLess(results["0"], num_shots * 0.6)
        self.assertGreater(results["1"], num_shots * 0.4)
        self.assertLess(results["1"], num_shots * 0.6)

if __name__ == "__main__":
    unittest.main()