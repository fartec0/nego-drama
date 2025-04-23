#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
Entanglement Preservation Module.
Provides utilities for tracking and preserving quantum entanglement during circuit operations.
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Union, Any
import logging
import networkx as nx

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector, partial_trace
except ImportError:
    logging.warning("Qiskit not installed. Limited entanglement functionality available.")


class EntanglementTracker:
    """
    Tracks entanglement between qubits during circuit construction and transformation.
    Maintains a graph representing entanglement relationships.
    """
    
    def __init__(self, num_qubits: int):
        """Initialize the entanglement tracker.
        
        Args:
            num_qubits: Number of qubits in the system
        """
        self.num_qubits = num_qubits
        self.logger = logging.getLogger(__name__)
        
        # Initialize entanglement graph
        self.entanglement_graph = nx.Graph()
        self.entanglement_graph.add_nodes_from(range(num_qubits))
        
        # Track entanglement strength (0.0 to 1.0)
        self.entanglement_strength = {}
        
        # Initialize operation history
        self.operation_history = []
        
    def update_from_gate(self, gate_name: str, target: int, control: Optional[int] = None) -> None:
        """Update entanglement tracking based on applied gate.
        
        Args:
            gate_name: Name of the quantum gate
            target: Target qubit index
            control: Control qubit index (optional)
        """
        # Record the operation
        self.operation_history.append({
            "gate": gate_name,
            "target": target,
            "control": control
        })
        
        # Update entanglement based on gate type
        if control is not None:
            # Two-qubit gates typically create or affect entanglement
            if gate_name in ["CNOT", "CX", "CZ", "CP", "SWAP"]:
                # These gates can create entanglement
                self._update_entanglement(control, target, gate_name)
        else:
            # Single-qubit gates don't create entanglement but might affect it
            if gate_name in ["H", "X", "Y", "Z", "S", "T"]:
                # Hadamard can affect entanglement when combined with other gates
                self._update_single_qubit_effects(target, gate_name)
                
    def update_from_circuit(self, circuit: 'QuantumCircuit') -> None:
        """Update entanglement tracking from a quantum circuit.
        
        Args:
            circuit: Quantum circuit with operations
        """
        try:
            # Extract operations from the circuit
            for instruction, qargs, cargs in circuit.data:
                gate_name = instruction.name
                
                # Extract target and control qubits
                if len(qargs) == 1:
                    # Single-qubit gate
                    target = qargs[0].index
                    self.update_from_gate(gate_name, target)
                elif len(qargs) == 2:
                    # Two-qubit gate
                    # For controlled gates, the first qubit is typically the control
                    control = qargs[0].index
                    target = qargs[1].index
                    self.update_from_gate(gate_name, target, control)
                    
        except Exception as e:
            self.logger.error(f"Error updating from circuit: {str(e)}")
            
    def update_from_statevector(self, statevector: Union[np.ndarray, 'Statevector']) -> None:
        """Update entanglement tracking directly from a statevector.
        
        Args:
            statevector: State vector of the quantum system
        """
        try:
            # Convert to numpy array if needed
            if hasattr(statevector, 'data'):
                sv_data = statevector.data
            else:
                sv_data = statevector
                
            # Reset entanglement graph
            self.entanglement_graph = nx.Graph()
            self.entanglement_graph.add_nodes_from(range(self.num_qubits))
            self.entanglement_strength = {}
            
            # Calculate entanglement for each pair of qubits
            for i in range(self.num_qubits):
                for j in range(i+1, self.num_qubits):
                    entanglement = self._calculate_entanglement(sv_data, i, j)
                    
                    # If there's significant entanglement, add an edge
                    if entanglement > 0.01:  # Threshold for numerical stability
                        self.entanglement_graph.add_edge(i, j)
                        self.entanglement_strength[(i, j)] = entanglement
                        self.logger.debug(f"Detected entanglement between qubits {i} and {j}: {entanglement:.4f}")
                        
        except Exception as e:
            self.logger.error(f"Error updating from statevector: {str(e)}")
    
    def get_entangled_pairs(self) -> List[Tuple[int, int]]:
        """Get all pairs of entangled qubits.
        
        Returns:
            List of tuples (qubit1, qubit2) representing entangled pairs
        """
        return list(self.entanglement_graph.edges())
        
    def get_entanglement_groups(self) -> List[Set[int]]:
        """Get groups of mutually entangled qubits (connected components).
        
        Returns:
            List of sets, where each set contains indices of entangled qubits
        """
        return [set(c) for c in nx.connected_components(self.entanglement_graph)]
        
    def is_entangled(self, qubit1: int, qubit2: int) -> bool:
        """Check if two qubits are entangled.
        
        Args:
            qubit1: First qubit index
            qubit2: Second qubit index
            
        Returns:
            True if the qubits are entangled, False otherwise
        """
        return self.entanglement_graph.has_edge(qubit1, qubit2)
        
    def get_entanglement_strength(self, qubit1: int, qubit2: int) -> float:
        """Get the entanglement strength between two qubits.
        
        Args:
            qubit1: First qubit index
            qubit2: Second qubit index
            
        Returns:
            Entanglement strength (0.0 to 1.0), or 0.0 if not entangled
        """
        if qubit1 > qubit2:
            qubit1, qubit2 = qubit2, qubit1
            
        return self.entanglement_strength.get((qubit1, qubit2), 0.0)
        
    def get_most_entangled_pair(self) -> Optional[Tuple[int, int]]:
        """Get the most strongly entangled pair of qubits.
        
        Returns:
            Tuple (qubit1, qubit2) of the most entangled pair, or None if no entanglement
        """
        if not self.entanglement_strength:
            return None
            
        return max(self.entanglement_strength.items(), key=lambda x: x[1])[0]
        
    def visualize_entanglement(self) -> Optional[Any]:
        """Generate a visualization of the entanglement graph.
        
        Returns:
            Matplotlib figure with the visualization, or None if matplotlib is not available
        """
        try:
            import matplotlib.pyplot as plt
            
            # Create figure
            plt.figure(figsize=(8, 6))
            
            # Draw the graph
            pos = nx.spring_layout(self.entanglement_graph)
            
            # Draw nodes
            nx.draw_networkx_nodes(self.entanglement_graph, pos, 
                                 node_color='lightblue', 
                                 node_size=500)
            
            # Draw edges with varying width based on entanglement strength
            edge_widths = []
            for u, v in self.entanglement_graph.edges():
                edge_widths.append(self.get_entanglement_strength(u, v) * 5)
                
            nx.draw_networkx_edges(self.entanglement_graph, pos, width=edge_widths)
            
            # Draw node labels
            nx.draw_networkx_labels(self.entanglement_graph, pos, font_size=12)
            
            # Draw edge labels (entanglement strength)
            edge_labels = {}
            for u, v in self.entanglement_graph.edges():
                edge_labels[(u, v)] = f"{self.get_entanglement_strength(u, v):.2f}"
                
            nx.draw_networkx_edge_labels(self.entanglement_graph, pos, edge_labels=edge_labels)
            
            plt.title("Quantum Entanglement Graph")
            plt.axis('off')
            plt.tight_layout()
            
            return plt.gcf()
            
        except ImportError:
            self.logger.warning("Matplotlib not available, skipping visualization")
            return None
            
    def _update_entanglement(self, control: int, target: int, gate_name: str) -> None:
        """Update entanglement graph based on two-qubit gate application.
        
        Args:
            control: Control qubit index
            target: Target qubit index
            gate_name: Name of the gate
        """
        if gate_name in ["CNOT", "CX", "CZ", "CP"]:
            # These gates can create entanglement between control and target
            
            # Simple model: If control and target are in different entanglement groups,
            # add an edge between them
            control_component = None
            target_component = None
            
            for component in nx.connected_components(self.entanglement_graph):
                if control in component:
                    control_component = component
                if target in component:
                    target_component = component
            
            # If they're in different components (or one/both not in any component)
            if control_component != target_component or control_component is None or target_component is None:
                self.entanglement_graph.add_edge(control, target)
                self.entanglement_strength[(min(control, target), max(control, target))] = 0.5  # Initial strength
                
        elif gate_name == "SWAP":
            # SWAP doesn't create entanglement but transfers it
            
            # Get all edges connected to control
            control_edges = list(self.entanglement_graph.edges(control))
            
            # Get all edges connected to target
            target_edges = list(self.entanglement_graph.edges(target))
            
            # Remove all these edges
            self.entanglement_graph.remove_edges_from(control_edges)
            self.entanglement_graph.remove_edges_from(target_edges)
            
            # Add swapped edges
            for u, v in control_edges:
                other = u if v == control else v
                if other != target:  # Avoid self-loops
                    self.entanglement_graph.add_edge(target, other)
                    self.entanglement_strength[(min(target, other), max(target, other))] = \
                        self.entanglement_strength.get((min(control, other), max(control, other)), 0.5)
                    
            for u, v in target_edges:
                other = u if v == target else v
                if other != control:  # Avoid self-loops
                    self.entanglement_graph.add_edge(control, other)
                    self.entanglement_strength[(min(control, other), max(control, other))] = \
                        self.entanglement_strength.get((min(target, other), max(target, other)), 0.5)
                    
    def _update_single_qubit_effects(self, target: int, gate_name: str) -> None:
        """Update entanglement effects from single-qubit gates.
        
        Args:
            target: Target qubit index
            gate_name: Name of the gate
        """
        # Most single-qubit gates preserve entanglement
        # Some gates (like measurements) can destroy entanglement,
        # but these would typically be handled separately
        pass
        
    def _calculate_entanglement(self, statevector: np.ndarray, qubit1: int, qubit2: int) -> float:
        """Calculate entanglement between two qubits using reduced density matrix.
        
        Args:
            statevector: Full statevector of the system
            qubit1: First qubit index
            qubit2: Second qubit index
            
        Returns:
            Measure of entanglement (0.0 to 1.0)
        """
        try:
            # Use partial_trace from Qiskit if available
            if 'partial_trace' in globals():
                # Convert to Statevector object if needed
                if not isinstance(statevector, Statevector):
                    statevector = Statevector(statevector)
                    
                # Qubits to keep
                keep_qubits = [qubit1, qubit2]
                
                # Qubits to trace out
                trace_qubits = [q for q in range(self.num_qubits) if q not in keep_qubits]
                
                # Get reduced density matrix
                rho_AB = partial_trace(statevector, trace_qubits)
                
                # Further trace out one qubit to get reduced state
                rho_A = partial_trace(rho_AB, [1])
                
                # Calculate linear entropy as entanglement measure
                # S_L = 1 - Tr(ρ²)
                entropy = 1.0 - np.real(np.trace(rho_A.data @ rho_A.data))
                
                # Normalize: for qubits, max linear entropy is 0.5
                entanglement = entropy / 0.5
                
                return entanglement
            else:
                # Fallback method when Qiskit isn't available
                # This is a simplified approach using the Schmidt decomposition
                
                # Reshape statevector to separate these two qubits
                tensor_dims = [2] * self.num_qubits
                reshaped_sv = statevector.reshape(tensor_dims)
                
                # Rearrange to put our qubits of interest first
                ax_order = list(range(self.num_qubits))
                ax_order.remove(qubit1)
                ax_order.remove(qubit2)
                ax_order = [qubit1, qubit2] + ax_order
                
                reshaped_sv = np.transpose(reshaped_sv, ax_order)
                
                # Reshape to group the two qubits vs rest
                reshaped_sv = reshaped_sv.reshape(4, -1)
                
                # Perform singular value decomposition
                u, s, vh = np.linalg.svd(reshaped_sv, full_matrices=False)
                
                # Normalize singular values
                s = s / np.linalg.norm(s)
                
                # Calculate entanglement using singular values
                # Using the Meyer-Wallach measure (equivalent to average linear entropy)
                entanglement = 1.0 - sum(sv**4 for sv in s)
                
                return entanglement
                
        except Exception as e:
            self.logger.error(f"Error calculating entanglement: {str(e)}")
            return 0.0


class EntanglementPreservingTransformer:
    """
    Transforms quantum circuits while preserving entanglement properties.
    """
    
    def __init__(self, circuit: Optional['QuantumCircuit'] = None):
        """Initialize the entanglement preserving transformer.
        
        Args:
            circuit: Initial quantum circuit (optional)
        """
        self.circuit = circuit
        self.logger = logging.getLogger(__name__)
        
        # Initialize tracker if circuit is provided
        if circuit is not None:
            self.tracker = EntanglementTracker(circuit.num_qubits)
            self.tracker.update_from_circuit(circuit)
        else:
            self.tracker = None
            
    def set_circuit(self, circuit: 'QuantumCircuit') -> None:
        """Set the circuit to transform.
        
        Args:
            circuit: Quantum circuit to transform
        """
        self.circuit = circuit
        self.tracker = EntanglementTracker(circuit.num_qubits)
        self.tracker.update_from_circuit(circuit)
        
    def optimize_circuit(self, optimization_level: int = 1) -> Optional['QuantumCircuit']:
        """Optimize the circuit while preserving entanglement.
        
        Args:
            optimization_level: Level of optimization (1-3)
            
        Returns:
            Optimized quantum circuit, or None if optimization failed
        """
        if self.circuit is None or self.tracker is None:
            self.logger.error("No circuit set for optimization")
            return None
            
        try:
            # Get initial entanglement properties
            initial_groups = self.tracker.get_entanglement_groups()
            
            # Create a copy of the circuit for optimization
            from qiskit import transpile
            
            # Apply optimization
            optimized = transpile(self.circuit, 
                                 optimization_level=optimization_level,
                                 basis_gates=['u1', 'u2', 'u3', 'cx'])
            
            # Check if entanglement is preserved
            check_tracker = EntanglementTracker(optimized.num_qubits)
            check_tracker.update_from_circuit(optimized)
            
            final_groups = check_tracker.get_entanglement_groups()
            
            # Verify that all originally entangled qubits remain entangled
            preserved = True
            for group in initial_groups:
                if len(group) > 1:  # Only check groups with entanglement
                    # Find corresponding group in final groups
                    found = False
                    for final_group in final_groups:
                        if group.issubset(final_group):
                            found = True
                            break
                    
                    if not found:
                        preserved = False
                        self.logger.warning(f"Entanglement not preserved for group {group}")
                        
            if not preserved:
                self.logger.warning("Entanglement was not preserved during optimization")
                # Fallback to lower optimization level or original circuit
                if optimization_level > 1:
                    self.logger.info(f"Trying optimization level {optimization_level-1}")
                    return self.optimize_circuit(optimization_level-1)
                else:
                    self.logger.info("Returning original circuit")
                    return self.circuit
                    
            return optimized
            
        except Exception as e:
            self.logger.error(f"Error during entanglement-preserving optimization: {str(e)}")
            return self.circuit
            
    def transpile_for_backend(self, 
                           backend_config: Dict[str, Any],
                           optimization_level: int = 1) -> Optional['QuantumCircuit']:
        """Transpile the circuit for a specific backend while preserving entanglement.
        
        Args:
            backend_config: Backend configuration
            optimization_level: Level of optimization
            
        Returns:
            Transpiled circuit, or None if transpilation failed
        """
        if self.circuit is None or self.tracker is None:
            self.logger.error("No circuit set for transpilation")
            return None
            
        try:
            # Get initial entanglement properties
            initial_groups = self.tracker.get_entanglement_groups()
            initial_pairs = self.tracker.get_entangled_pairs()
            
            # Extract backend properties
            basis_gates = backend_config.get('basis_gates', ['u1', 'u2', 'u3', 'cx'])
            coupling_map = backend_config.get('coupling_map', None)
            
            # Create a copy of the circuit for transpilation
            from qiskit import transpile
            
            # Apply transpilation
            transpiled = transpile(self.circuit,
                                 basis_gates=basis_gates,
                                 coupling_map=coupling_map,
                                 optimization_level=optimization_level)
            
            # Check if entanglement is preserved
            check_tracker = EntanglementTracker(transpiled.num_qubits)
            check_tracker.update_from_circuit(transpiled)
            
            # Verify original entanglement is preserved
            all_preserved = True
            for q1, q2 in initial_pairs:
                # Check if this pair is still entangled (directly or indirectly)
                preserved = False
                for group in check_tracker.get_entanglement_groups():
                    if q1 in group and q2 in group:
                        preserved = True
                        break
                
                if not preserved:
                    all_preserved = False
                    self.logger.warning(f"Entanglement between qubits {q1} and {q2} was not preserved")
            
            if not all_preserved:
                self.logger.warning("Some entanglement was not preserved during transpilation")
                # Consider fallback strategies or returning original circuit
                
            return transpiled
            
        except Exception as e:
            self.logger.error(f"Error during entanglement-preserving transpilation: {str(e)}")
            return self.circuit
            
    def detect_operations_affecting_entanglement(self) -> List[Dict[str, Any]]:
        """Detect operations that create or destroy entanglement.
        
        Returns:
            List of operations that affect entanglement
        """
        if self.circuit is None:
            self.logger.error("No circuit set for analysis")
            return []
            
        try:
            # Analyze circuit operations
            affecting_ops = []
            tracker = EntanglementTracker(self.circuit.num_qubits)
            
            for idx, (instruction, qargs, cargs) in enumerate(self.circuit.data):
                # Record previous state
                prev_pairs = set(tracker.get_entangled_pairs())
                
                # Apply operation
                if len(qargs) == 1:
                    # Single-qubit gate
                    tracker.update_from_gate(instruction.name, qargs[0].index)
                elif len(qargs) == 2:
                    # Two-qubit gate
                    tracker.update_from_gate(instruction.name, qargs[1].index, qargs[0].index)
                    
                # Record new state
                new_pairs = set(tracker.get_entangled_pairs())
                
                # Check if entanglement changed
                if prev_pairs != new_pairs:
                    # This operation affected entanglement
                    affecting_ops.append({
                        "index": idx,
                        "gate": instruction.name,
                        "qubits": [q.index for q in qargs],
                        "created": len(new_pairs - prev_pairs),
                        "destroyed": len(prev_pairs - new_pairs)
                    })
                    
            return affecting_ops
            
        except Exception as e:
            self.logger.error(f"Error detecting entanglement-affecting operations: {str(e)}")
            return []