#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
DeepChecks UI components for quantum-related validation and monitoring.
These components provide data validation, model monitoring, and circuit parameter validation
specifically designed for quantum computing applications.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Callable

import gradio as gr

from src.ui.integrations.deepchecks import DeepChecksIntegration

class QuantumDataValidator:
    """Gradio component for validating data used in quantum algorithms."""
    
    def __init__(self, integration: Optional[DeepChecksIntegration] = None):
        """Initialize the quantum data validator component.
        
        Args:
            integration: DeepChecks integration instance
        """
        self.integration = integration or DeepChecksIntegration()
        self.logger = logging.getLogger(__name__)
        
    def build(self) -> gr.Blocks:
        """Build the Gradio interface for quantum data validation.
        
        Returns:
            Gradio Blocks interface
        """
        self.logger.info("Building quantum data validation component")
        
        validate_fn, inputs, outputs = self.integration.create_data_validation_interface(
            default_checks=["duplicates", "multivariate_drift"]
        )
        
        with gr.Blocks() as interface:
            gr.Markdown("# Quantum Data Validation")
            gr.Markdown("""
            Validate classical data before using it in quantum algorithms.
            This tool helps ensure your data is clean and properly formatted before quantum processing.
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Input Data")
                    file_input = inputs[0]
                    label_input = inputs[1]
                    catfeatures_input = inputs[2]
                    checks_input = inputs[3]
                    
                    validate_button = gr.Button("Validate Data")
                
                with gr.Column():
                    gr.Markdown("## Validation Results")
                    summary_output = outputs[0]
                    report_output = outputs[1]
            
            validate_button.click(
                fn=validate_fn,
                inputs=[file_input, label_input, catfeatures_input, checks_input],
                outputs=[summary_output, report_output]
            )
            
            gr.Markdown("""
            ### Recommended Checks for Quantum Data
            
            - **Duplicates**: Duplicated data can skew quantum feature embeddings
            - **Multivariate Drift**: Detects distribution shifts that may affect quantum circuit parameters
            - **Data Integrity**: Ensures data is clean before quantum processing
            
            For best results with quantum algorithms, ensure data is:
            1. Normalized between 0 and 1 for angle encoding
            2. Free of outliers that could cause extreme rotations
            3. Balanced for classification tasks
            """)
        
        return interface


class QuantumModelMonitor:
    """Gradio component for monitoring quantum-enhanced ML models."""
    
    def __init__(self, integration: Optional[DeepChecksIntegration] = None):
        """Initialize the quantum model monitor component.
        
        Args:
            integration: DeepChecks integration instance
        """
        self.integration = integration or DeepChecksIntegration()
        self.logger = logging.getLogger(__name__)
        
    def build(self) -> gr.Blocks:
        """Build the Gradio interface for quantum model monitoring.
        
        Returns:
            Gradio Blocks interface
        """
        self.logger.info("Building quantum model monitoring component")
        
        monitor_fn, inputs, outputs = self.integration.create_model_monitoring_interface()
        
        with gr.Blocks() as interface:
            gr.Markdown("# Quantum-Enhanced Model Monitoring")
            gr.Markdown("""
            Monitor the performance of quantum-enhanced machine learning models.
            This tool helps detect data drift that may affect model performance.
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Model & Data Information")
                    reference_input = inputs[0]
                    current_input = inputs[1]
                    label_input = inputs[2]
                    catfeatures_input = inputs[3]
                    model_type_input = inputs[4]
                    
                    monitor_button = gr.Button("Check for Drift")
                
                with gr.Column():
                    gr.Markdown("## Monitoring Results")
                    summary_output = outputs[0]
                    report_output = outputs[1]
            
            monitor_button.click(
                fn=monitor_fn,
                inputs=[reference_input, current_input, label_input, catfeatures_input, model_type_input],
                outputs=[summary_output, report_output]
            )
            
            gr.Markdown("""
            ### Why Monitor Quantum-Enhanced Models?
            
            Quantum-enhanced models can be particularly sensitive to data drift because:
            
            1. **Parameter Sensitivity**: Small changes in input data can cause large shifts in quantum circuit parameters
            2. **Entanglement Effects**: Data distribution shifts can affect entanglement patterns
            3. **Noise Amplification**: Drift in features can amplify quantum noise effects
            
            Regular monitoring ensures your hybrid quantum-classical models maintain performance over time.
            """)
        
        return interface


class QuantumCircuitValidator:
    """Gradio component for validating quantum circuit parameters."""
    
    def __init__(self, integration: Optional[DeepChecksIntegration] = None):
        """Initialize the quantum circuit validator component.
        
        Args:
            integration: DeepChecks integration instance
        """
        self.integration = integration or DeepChecksIntegration()
        self.logger = logging.getLogger(__name__)
        
    def build(self) -> gr.Blocks:
        """Build the Gradio interface for quantum circuit parameter validation.
        
        Returns:
            Gradio Blocks interface
        """
        self.logger.info("Building quantum circuit parameter validation component")
        
        validate_fn, inputs, outputs = self.integration.create_quantum_parameter_validation_interface()
        
        with gr.Blocks() as interface:
            gr.Markdown("# Quantum Circuit Parameter Validation")
            gr.Markdown("""
            Validate parameters used in quantum circuits to detect anomalies.
            This tool helps identify parameter values that may cause instability or unexpected behavior.
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Circuit Parameters")
                    parameters_input = inputs[0]
                    names_input = inputs[1]
                    threshold_input = inputs[2]
                    
                    example_button = gr.Button("Load Example")
                    validate_button = gr.Button("Validate Parameters")
                
                with gr.Column():
                    gr.Markdown("## Validation Results")
                    results_output = outputs[0]
            
            # Example parameter set for quantum circuits
            def load_example():
                params = "0.1, 1.57, 0.78, 0.2, 10.5, 0.3"
                names = "rx_angle, ry_angle, rz_angle, cx_weight, anomaly_param, entanglement_factor"
                return params, names
            
            example_button.click(
                fn=load_example,
                inputs=[],
                outputs=[parameters_input, names_input]
            )
            
            validate_button.click(
                fn=validate_fn,
                inputs=[parameters_input, names_input, threshold_input],
                outputs=[results_output]
            )
            
            gr.Markdown("""
            ### Circuit Parameter Guidelines
            
            - **Rotation angles**: Typically between 0 and 2π
            - **Entanglement parameters**: Usually small values (0.1-1.0)
            - **Circuit depth factors**: Avoid values that lead to very deep circuits
            
            The validation uses statistical analysis to detect outliers that may cause:
            1. Barren plateaus in training landscapes
            2. Excessive circuit depth
            3. Numerical instability in simulations
            """)
        
        return interface