#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quantum UI utility helpers.
This module provides utility functions to connect quantum modules with UI components.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Tuple, Optional

from src.quantum.simulators.quantum_simulator import QuantumSimulator
from src.quantum.visualization.state_visualizer import StateVisualizer
from src.quantum.algorithms.grovers_algorithm import GroversAlgorithm

def parse_circuit_data(circuit_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse circuit data from UI format to quantum simulator format.
    
    Args:
        circuit_data: Circuit data from UI
        
    Returns:
        Formatted circuit data for quantum simulator
    """
    parsed_data = []
    
    for operation in circuit_data:
        parsed_op = {
            "gate": operation["gate"],
            "target": int(operation["target"])
        }
        
        if "control" in operation and operation["control"] != "None":
            parsed_op["control"] = int(operation["control"])
            
        parsed_data.append(parsed_op)
        
    return parsed_data

def run_circuit_simulation(
    circuit_data: List[Dict[str, Any]], 
    num_qubits: int,
    num_shots: int = 1024
) -> Dict[str, Any]:
    """
    Run a quantum circuit simulation.
    
    Args:
        circuit_data: Circuit operations data
        num_qubits: Number of qubits in the circuit
        num_shots: Number of measurement shots
        
    Returns:
        Simulation results
    """
    # Initialize simulator
    simulator = QuantumSimulator(num_qubits)
    
    # Parse circuit data
    parsed_circuit = parse_circuit_data(circuit_data)
    
    # Apply circuit
    simulator.apply_circuit(parsed_circuit)
    
    # Get state vector
    state_vector = simulator.get_statevector()
    
    # Perform measurements
    measurement_results = simulator.measure(num_shots)
    
    # Create visualizations
    prob_fig = StateVisualizer.plot_probabilities(state_vector, num_qubits)
    phase_fig = StateVisualizer.plot_phase(state_vector, num_qubits)
    measurement_fig = StateVisualizer.plot_measurement_results(measurement_results, num_shots)
    
    # If it's a single qubit or system has few qubits, also show Bloch sphere
    bloch_figs = []
    if num_qubits <= 3:
        for i in range(num_qubits):
            bloch_fig = StateVisualizer.plot_bloch_sphere(state_vector, i)
            bloch_figs.append(bloch_fig)
    
    # Return results
    return {
        "state_vector": state_vector.tolist(),
        "probabilities": simulator.get_probabilities().tolist(),
        "measurement_results": measurement_results,
        "num_qubits": num_qubits,
        "num_shots": num_shots,
        "visualizations": {
            "probability": prob_fig,
            "phase": phase_fig,
            "measurement": measurement_fig,
            "bloch": bloch_figs
        }
    }

def run_algorithm(
    algorithm_name: str,
    params: Dict[str, Any],
    num_shots: int = 1024
) -> Dict[str, Any]:
    """
    Run a quantum algorithm.
    
    Args:
        algorithm_name: Name of the algorithm to run
        params: Algorithm parameters
        num_shots: Number of measurement shots
        
    Returns:
        Algorithm results
    """
    results = {}
    
    # Grover's Algorithm
    if algorithm_name == "Grover's Algorithm":
        num_elements = params.get("elements", 4)
        marked_element = params.get("marked_element", None)
        
        # Calculate number of qubits required
        num_qubits = max(1, int(np.ceil(np.log2(num_elements))))
        
        # Initialize algorithm
        grover = GroversAlgorithm(num_qubits, marked_element)
        
        # Run algorithm
        algo_results = grover.run()
        
        # Create visualization
        results_fig = grover.visualize_results(algo_results)
        
        # Return results
        results = {
            "algorithm": "Grover's Algorithm",
            "num_qubits": num_qubits,
            "marked_element": algo_results["marked_element"],
            "most_probable": algo_results["most_probable"],
            "success": algo_results["success"],
            "optimal_iterations": algo_results["optimal_iterations"],
            "probabilities": algo_results["probabilities"].tolist(),
            "visualization": results_fig
        }
        
    # Quantum Fourier Transform
    elif algorithm_name == "Quantum Fourier Transform":
        # Implement QFT
        pass
        
    # Shor's Algorithm
    elif algorithm_name == "Shor's Algorithm":
        # Implement Shor's algorithm
        pass
        
    # VQE
    elif algorithm_name == "VQE":
        # Implement VQE
        pass
        
    return results

def format_state_vector(state_vector: np.ndarray, num_qubits: int, threshold: float = 1e-10) -> str:
    """
    Format a state vector for display in the UI.
    
    Args:
        state_vector: Quantum state vector
        num_qubits: Number of qubits
        threshold: Amplitude threshold for display
        
    Returns:
        Formatted string representation of the state vector
    """
    formatted = []
    
    for i, amplitude in enumerate(state_vector):
        if abs(amplitude) > threshold:
            # Format complex number
            if amplitude.imag >= 0:
                amp_str = f"{amplitude.real:.4f} + {amplitude.imag:.4f}i"
            else:
                amp_str = f"{amplitude.real:.4f} - {abs(amplitude.imag):.4f}i"
                
            # Format basis state
            basis = f"|{bin(i)[2:].zfill(num_qubits)}⟩"
            
            formatted.append(f"({amp_str}) {basis}")
    
    if not formatted:
        return "State vector has no significant amplitudes above threshold."
        
    return " + ".join(formatted)