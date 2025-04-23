#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
Circuit Builder Component for the Quantum UI.
This component allows users to visually construct quantum circuits.
"""

import gradio as gr
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

class CircuitBuilderComponent:
    """A component for building quantum circuits visually."""
    
    def __init__(self, max_qubits: int = 10):
        """Initialize the circuit builder component.
        
        Args:
            max_qubits: Maximum number of qubits supported
        """
        self.max_qubits = max_qubits
        self.circuit_data = []
        
    def build_interface(self) -> List[gr.Component]:
        """Build the Gradio interface components.
        
        Returns:
            List of Gradio components that make up this component
        """
        with gr.Row() as row:
            with gr.Column(scale=3):
                num_qubits = gr.Slider(
                    minimum=1,
                    maximum=self.max_qubits,
                    value=3,
                    step=1,
                    label="Number of Qubits"
                )
                
                gate_selector = gr.Dropdown(
                    choices=["H", "X", "Y", "Z", "S", "T", "CNOT", "SWAP", "Toffoli"],
                    value="H",
                    label="Gate"
                )
                
                qubit_selector = gr.Dropdown(
                    choices=[str(i) for i in range(3)], 
                    value="0",
                    label="Target Qubit"
                )
                
                control_selector = gr.Dropdown(
                    choices=["None"] + [str(i) for i in range(3)],
                    value="None",
                    label="Control Qubit",
                    visible=False
                )
                
                add_gate_btn = gr.Button("Add Gate")
                
            with gr.Column(scale=7):
                circuit_display = gr.HTML(
                    "<div class='circuit-display'>Circuit will appear here</div>",
                    label="Quantum Circuit"
                )
                
                circuit_code = gr.Code(
                    language="python",
                    value="# Quantum circuit code will appear here",
                    label="Circuit Code"
                )
        
        # Update available qubits when num_qubits changes
        def update_qubit_options(num_qubits):
            options = [str(i) for i in range(int(num_qubits))]
            return {
                qubit_selector: gr.Dropdown(choices=options, value=options[0] if options else "0"),
                control_selector: gr.Dropdown(choices=["None"] + options, value="None")
            }
        
        num_qubits.change(
            update_qubit_options,
            inputs=[num_qubits],
            outputs=[qubit_selector, control_selector]
        )
        
        # Show/hide control qubit selector based on gate type
        def update_control_visibility(gate):
            return {
                control_selector: gr.Dropdown(visible=gate in ["CNOT", "Toffoli", "SWAP"])
            }
            
        gate_selector.change(
            update_control_visibility,
            inputs=[gate_selector],
            outputs=[control_selector]
        )
        
        # Add gate to circuit
        def add_gate_to_circuit(gate, target, control, num_qubits, current_display):
            # Here you would add the gate to your circuit data structure
            # and generate an updated circuit visualization
            
            # For demonstration, just return some HTML
            control_str = "" if control == "None" else f", control={control}"
            new_gate = f"<div>Added {gate} to qubit {target}{control_str}</div>"
            
            if "Circuit will appear here" in current_display:
                current_display = ""
                
            updated_display = current_display + new_gate
            
            # Generate code for the circuit
            code = f"""
# Quantum circuit with {num_qubits} qubits
from qiskit import QuantumCircuit

qc = QuantumCircuit({num_qubits})
# Assuming the circuit has gates added
qc.{gate.lower()}({target}{control_str})
            """
            
            return {
                circuit_display: updated_display,
                circuit_code: code
            }
            
        add_gate_btn.click(
            add_gate_to_circuit,
            inputs=[gate_selector, qubit_selector, control_selector, num_qubits, circuit_display],
            outputs=[circuit_display, circuit_code]
        )
        
        return [row]
    
    def get_circuit_data(self) -> Dict[str, Any]:
        """Get the current circuit data.
        
        Returns:
            Dictionary containing the current circuit data
        """
        return {
            "circuit": self.circuit_data,
            "num_qubits": len(set(gate["target"] for gate in self.circuit_data))
        }