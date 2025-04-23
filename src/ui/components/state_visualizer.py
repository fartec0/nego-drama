#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
State Visualizer Component for the Quantum UI.
This component visualizes quantum states using various representations.
"""

import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Tuple, Optional

class StateVisualizerComponent:
    """A component for visualizing quantum states."""
    
    def __init__(self):
        """Initialize the state visualizer component."""
        self.current_state = None
        
    def build_interface(self) -> List[gr.Component]:
        """Build the Gradio interface components.
        
        Returns:
            List of Gradio components that make up this component
        """
        with gr.Row() as row:
            with gr.Column():
                visualization_type = gr.Dropdown(
                    choices=["Bloch Sphere", "Probability Distribution", "Matrix View", "Circuit Output"],
                    value="Probability Distribution",
                    label="Visualization Type"
                )
                
                run_simulation_btn = gr.Button("Run Simulation")
                
            with gr.Column():
                visualization_output = gr.Plot(
                    label="Quantum State Visualization"
                )
                
                state_info = gr.JSON(
                    label="State Information",
                    value={"state": "Not simulated yet"}
                )
        
        # Example simulation function (placeholder)
        def run_simulation(viz_type):
            # This would normally take circuit data from the circuit builder
            # and run a quantum simulation
            
            # For demonstration, just return a simple visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if viz_type == "Probability Distribution":
                # Generate example probability distribution for a 3-qubit system
                states = range(8)  # 2^3 states
                probabilities = np.random.random(8)
                probabilities = probabilities / np.sum(probabilities)  # Normalize
                
                ax.bar(states, probabilities)
                ax.set_xlabel("Computational Basis States")
                ax.set_ylabel("Probability")
                ax.set_title("Quantum State Probability Distribution")
                ax.set_xticks(states)
                ax.set_xticklabels([f"|{bin(i)[2:].zfill(3)}>>" for i in states])
                
                state_data = {
                    "state_type": "probability_distribution",
                    "num_qubits": 3,
                    "probabilities": {f"|{bin(i)[2:].zfill(3)}>": float(p) for i, p in enumerate(probabilities)}
                }
                
            elif viz_type == "Bloch Sphere":
                # Example Bloch sphere for a single qubit (simplified representation)
                theta = np.linspace(0, 2*np.pi, 100)
                x = np.sin(theta)
                y = np.cos(theta)
                
                ax.plot(x, y, 'b-')
                ax.set_xlabel("X")
                ax.set_ylabel("Y")
                ax.set_title("Bloch Sphere Representation (2D projection)")
                ax.set_aspect('equal')
                
                # Example state vector
                state_angle = np.random.random() * 2 * np.pi
                ax.arrow(0, 0, np.sin(state_angle) * 0.8, np.cos(state_angle) * 0.8, 
                         head_width=0.05, head_length=0.1, fc='r', ec='r')
                
                state_data = {
                    "state_type": "bloch_sphere",
                    "num_qubits": 1,
                    "theta": float(state_angle),
                    "phi": 0.0
                }
                
            else:
                # Generic placeholder
                ax.text(0.5, 0.5, f"{viz_type} visualization would appear here", 
                        ha='center', va='center', fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
                
                state_data = {
                    "state_type": viz_type.lower().replace(" ", "_"),
                    "message": "Visualization not implemented yet"
                }
            
            return {
                visualization_output: fig,
                state_info: state_data
            }
            
        run_simulation_btn.click(
            run_simulation,
            inputs=[visualization_type],
            outputs=[visualization_output, state_info]
        )
        
        return [row]
    
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Update the current quantum state.
        
        Args:
            new_state: New quantum state data
        """
        self.current_state = new_state