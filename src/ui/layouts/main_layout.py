#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main layout for the Quantum UI application.
This module defines the overall layout of the application UI.
"""

import gradio as gr
from typing import Dict, Any

from src.ui.components.circuit_builder import CircuitBuilderComponent
from src.ui.components.state_visualizer import StateVisualizerComponent
from src.config.settings.app_settings import AppSettings

def create_main_layout(settings: AppSettings) -> gr.Blocks:
    """Create the main layout for the Quantum UI application.
    
    Args:
        settings: Application settings
        
    Returns:
        Gradio Blocks interface
    """
    with gr.Blocks(title=settings.app_name, theme=settings.theme) as app:
        gr.Markdown(f"# {settings.app_name}")
        gr.Markdown("A professional-grade quantum computing interface built with Gradio")
        
        with gr.Tabs():
            with gr.TabItem("Circuit Designer"):
                circuit_builder = CircuitBuilderComponent(max_qubits=settings.max_qubits)
                circuit_builder.build_interface()
                
            with gr.TabItem("State Visualization"):
                state_visualizer = StateVisualizerComponent()
                state_visualizer.build_interface()
                
            with gr.TabItem("Quantum Algorithms"):
                with gr.Row():
                    with gr.Column():
                        algorithm_selector = gr.Dropdown(
                            choices=["Grover's Algorithm", "Quantum Fourier Transform", "Shor's Algorithm", "VQE"],
                            value="Grover's Algorithm",
                            label="Select Algorithm"
                        )
                        
                        run_algorithm_btn = gr.Button("Run Algorithm")
                        
                    with gr.Column():
                        algorithm_description = gr.Markdown(
                            "**Grover's Algorithm** is a quantum algorithm for unstructured search that finds with high probability the unique input to a black box function that produces a particular output value, using just O(√N) evaluations of the function, where N is the size of the function's domain."
                        )
                        
                        algorithm_params = gr.JSON(
                            {"elements": 4, "marked_element": 2},
                            label="Algorithm Parameters"
                        )
                
                algorithm_results = gr.Plot(label="Algorithm Results")
            
            with gr.TabItem("Settings"):
                with gr.Row():
                    with gr.Column():
                        backend_selector = gr.Dropdown(
                            choices=list(settings.available_backends.keys()),
                            value=list(settings.available_backends.keys())[0],
                            label="Quantum Backend"
                        )
                        
                        shots = gr.Slider(
                            minimum=1,
                            maximum=10000,
                            value=settings.default_shots,
                            step=1,
                            label="Number of Shots"
                        )
                        
                    with gr.Column():
                        backend_info = gr.JSON(
                            settings.available_backends[list(settings.available_backends.keys())[0]],
                            label="Backend Information"
                        )
        
        # Update backend info when selected
        def update_backend_info(backend_name):
            return settings.available_backends.get(backend_name, {"name": "Unknown", "description": "No information available"})
            
        backend_selector.change(
            update_backend_info,
            inputs=[backend_selector],
            outputs=[backend_info]
        )
        
        # Update algorithm description when selected
        def update_algorithm_description(algorithm_name):
            descriptions = {
                "Grover's Algorithm": "**Grover's Algorithm** is a quantum algorithm for unstructured search that finds with high probability the unique input to a black box function that produces a particular output value, using just O(√N) evaluations of the function, where N is the size of the function's domain.",
                "Quantum Fourier Transform": "**Quantum Fourier Transform (QFT)** is a linear transformation on quantum bits, and is the quantum analogue of the discrete Fourier transform. It is a key component of many quantum algorithms.",
                "Shor's Algorithm": "**Shor's Algorithm** is a quantum algorithm for integer factorization, formulated in 1994. It solves the factoring problem more efficiently than the best-known classical algorithm.",
                "VQE": "**Variational Quantum Eigensolver (VQE)** is a hybrid quantum-classical algorithm used for finding eigenvalues of a matrix, usually a Hamiltonian of a quantum system."
            }
            
            params = {
                "Grover's Algorithm": {"elements": 4, "marked_element": 2},
                "Quantum Fourier Transform": {"register_size": 3},
                "Shor's Algorithm": {"number_to_factor": 15},
                "VQE": {"hamiltonian": "Hydrogen molecule", "max_iterations": 100}
            }
            
            return descriptions.get(algorithm_name, "No description available"), params.get(algorithm_name, {})
            
        algorithm_selector.change(
            update_algorithm_description,
            inputs=[algorithm_selector],
            outputs=[algorithm_description, algorithm_params]
        )
        
    return app