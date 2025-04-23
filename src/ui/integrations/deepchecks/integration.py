#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
DeepChecks integration for Gradio UI components.
Provides utility functions for connecting DeepChecks validation to Gradio interfaces.
"""

import os
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union, Callable, Tuple

import gradio as gr
import numpy as np
import pandas as pd
from deepchecks.tabular import Dataset
from deepchecks.tabular.checks import MultivariateDrift, DataDuplicates

from src.core.services.deepchecks.deepchecks_service import DeepChecksService

class DeepChecksIntegration:
    """Integration layer between DeepChecks validation and Gradio UI."""
    
    def __init__(self, service: Optional[DeepChecksService] = None):
        """Initialize the DeepChecks integration.
        
        Args:
            service: DeepChecks service instance
        """
        self.service = service or DeepChecksService()
        self.logger = logging.getLogger(__name__)
        self._temp_report_dir = tempfile.mkdtemp(prefix="deepchecks_reports_")
        
    def create_data_validation_interface(
        self, 
        default_checks: Optional[List[str]] = None
    ) -> Tuple[Callable, List[gr.components.Component], List[gr.components.Component]]:
        """Create a Gradio interface for data validation.
        
        Args:
            default_checks: List of default check names to run
            
        Returns:
            Tuple of (inference function, input components, output components)
        """
        self.logger.info("Creating data validation interface")
        
        available_checks = {
            "duplicates": DataDuplicates(),
            "multivariate_drift": MultivariateDrift(),
            # Add more checks as needed
        }
        
        # Define the validation function
        def validate_data(
            csv_file: Union[str, tempfile._TemporaryFileWrapper],
            label_column: str,
            cat_features: str,
            check_names: List[str]
        ) -> Tuple[str, str]:
            try:
                # Parse categorical features
                cat_features_list = [f.strip() for f in cat_features.split(',')] if cat_features else None
                
                # Load data
                if isinstance(csv_file, str):
                    df = pd.read_csv(csv_file)
                else:
                    df = pd.read_csv(csv_file.name)
                
                # Create dataset
                dataset = self.service.create_tabular_dataset(
                    df=df,
                    label_name=label_column if label_column else None,
                    cat_features=cat_features_list
                )
                
                # Get checks to run
                checks_to_run = [available_checks[name] for name in check_names if name in available_checks]
                
                # Validate data
                result = self.service.validate_quantum_input_data(dataset, checks=checks_to_run)
                
                # Create summary
                summary = f"## Data Validation Summary\n\n"
                summary += f"- Dataset shape: {df.shape}\n"
                summary += f"- Label column: {label_column}\n"
                summary += f"- Categorical features: {cat_features_list}\n\n"
                
                passed_checks = []
                failed_checks = []
                
                for check in result.get_check_objects():
                    if check.passed():
                        passed_checks.append(f"- ✅ {check.name()}")
                    else:
                        failed_checks.append(f"- ❌ {check.name()}: {check.get_header()}")
                
                summary += "### Passed Checks\n"
                summary += "\n".join(passed_checks) + "\n\n"
                
                summary += "### Failed Checks\n"
                summary += "\n".join(failed_checks) + "\n\n"
                
                # Generate HTML report
                report_path = os.path.join(self._temp_report_dir, "data_validation_report.html")
                self.service.generate_html_report(result, report_path)
                
                return summary, report_path
                
            except Exception as e:
                self.logger.error(f"Error in data validation: {str(e)}")
                return f"Error: {str(e)}", ""
        
        # Define Gradio components
        input_components = [
            gr.File(label="CSV Data File"),
            gr.Textbox(label="Label Column (optional)"),
            gr.Textbox(label="Categorical Features (comma-separated, optional)"),
            gr.CheckboxGroup(
                choices=list(available_checks.keys()),
                value=default_checks or list(available_checks.keys()),
                label="Checks to Run"
            )
        ]
        
        output_components = [
            gr.Markdown(label="Validation Summary"),
            gr.HTML(label="Detailed Report")
        ]
        
        return validate_data, input_components, output_components
    
    def create_model_monitoring_interface(
        self
    ) -> Tuple[Callable, List[gr.components.Component], List[gr.components.Component]]:
        """Create a Gradio interface for model monitoring of quantum-enhanced ML models.
        
        Returns:
            Tuple of (inference function, input components, output components)
        """
        self.logger.info("Creating model monitoring interface")
        
        # Define the monitoring function
        def monitor_model(
            reference_csv: Union[str, tempfile._TemporaryFileWrapper],
            current_csv: Union[str, tempfile._TemporaryFileWrapper],
            label_column: str,
            cat_features: str,
            model_type: str
        ) -> Tuple[str, str]:
            try:
                # Parse categorical features
                cat_features_list = [f.strip() for f in cat_features.split(',')] if cat_features else None
                
                # Load data
                if isinstance(reference_csv, str):
                    reference_df = pd.read_csv(reference_csv)
                else:
                    reference_df = pd.read_csv(reference_csv.name)
                    
                if isinstance(current_csv, str):
                    current_df = pd.read_csv(current_csv)
                else:
                    current_df = pd.read_csv(current_csv.name)
                
                # Create datasets
                reference_dataset = self.service.create_tabular_dataset(
                    df=reference_df,
                    label_name=label_column if label_column else None,
                    cat_features=cat_features_list,
                    dataset_name="Reference"
                )
                
                current_dataset = self.service.create_tabular_dataset(
                    df=current_df,
                    label_name=label_column if label_column else None,
                    cat_features=cat_features_list,
                    dataset_name="Current"
                )
                
                # Check for drift
                result = self.service.check_dataset_drift(reference_dataset, current_dataset)
                
                # Create summary
                summary = f"## Model Monitoring Summary\n\n"
                summary += f"- Reference dataset shape: {reference_df.shape}\n"
                summary += f"- Current dataset shape: {current_df.shape}\n"
                summary += f"- Model type: {model_type}\n\n"
                
                # Summarize drift checks
                drift_detected = False
                for check in result.get_check_objects():
                    if not check.passed():
                        drift_detected = True
                        summary += f"- ⚠️ {check.name()}: Drift detected\n"
                
                if not drift_detected:
                    summary += "✅ No significant data drift detected\n\n"
                else:
                    summary += "\n⚠️ Data drift detected. This may affect your quantum-enhanced ML model's performance.\n\n"
                
                # Generate HTML report
                report_path = os.path.join(self._temp_report_dir, "model_monitoring_report.html")
                self.service.generate_html_report(result, report_path)
                
                return summary, report_path
                
            except Exception as e:
                self.logger.error(f"Error in model monitoring: {str(e)}")
                return f"Error: {str(e)}", ""
        
        # Define Gradio components
        input_components = [
            gr.File(label="Reference Data (CSV)"),
            gr.File(label="Current Data (CSV)"),
            gr.Textbox(label="Label Column"),
            gr.Textbox(label="Categorical Features (comma-separated, optional)"),
            gr.Radio(
                choices=["Quantum-Enhanced Classifier", "Quantum-Enhanced Regressor", "Hybrid Model"],
                value="Quantum-Enhanced Classifier",
                label="Model Type"
            )
        ]
        
        output_components = [
            gr.Markdown(label="Monitoring Summary"),
            gr.HTML(label="Detailed Report")
        ]
        
        return monitor_model, input_components, output_components
    
    def create_quantum_parameter_validation_interface(
        self
    ) -> Tuple[Callable, List[gr.components.Component], List[gr.components.Component]]:
        """Create a Gradio interface for validating quantum circuit parameters.
        
        Returns:
            Tuple of (inference function, input components, output components)
        """
        self.logger.info("Creating quantum parameter validation interface")
        
        # Define the validation function
        def validate_parameters(
            parameters_str: str,
            parameter_names_str: str,
            threshold: float
        ) -> str:
            try:
                # Parse parameters and names
                parameters = np.array([float(p.strip()) for p in parameters_str.split(',')])
                parameter_names = [n.strip() for n in parameter_names_str.split(',')]
                
                if len(parameters) != len(parameter_names):
                    return f"Error: Number of parameters ({len(parameters)}) doesn't match number of names ({len(parameter_names)})"
                
                # Detect anomalies
                anomalies = self.service.detect_parameter_anomalies(
                    parameters=parameters,
                    parameter_names=parameter_names,
                    threshold=threshold
                )
                
                # Create summary
                summary = f"## Quantum Parameter Validation\n\n"
                summary += f"- Parameters analyzed: {len(parameters)}\n"
                summary += f"- Anomaly threshold (Z-score): {threshold}\n\n"
                
                summary += "### Parameter Analysis\n\n"
                summary += "| Parameter | Value | Status |\n"
                summary += "|-----------|-------|---------|\n"
                
                for name, is_anomaly in anomalies.items():
                    idx = parameter_names.index(name)
                    value = parameters[idx]
                    status = "❌ ANOMALY" if is_anomaly else "✅ NORMAL"
                    summary += f"| {name} | {value:.4f} | {status} |\n"
                
                anomaly_count = sum(1 for v in anomalies.values() if v)
                if anomaly_count > 0:
                    summary += f"\n⚠️ {anomaly_count} parameter anomalies detected. "
                    summary += "These may affect the performance of your quantum circuit.\n"
                else:
                    summary += "\n✅ All parameters are within normal ranges.\n"
                
                return summary
                
            except Exception as e:
                self.logger.error(f"Error in parameter validation: {str(e)}")
                return f"Error: {str(e)}"
        
        # Define Gradio components
        input_components = [
            gr.Textbox(lines=3, label="Parameters (comma-separated)"),
            gr.Textbox(lines=3, label="Parameter Names (comma-separated)"),
            gr.Slider(minimum=1.0, maximum=5.0, value=3.0, step=0.1, label="Anomaly Threshold (Z-score)")
        ]
        
        output_components = [
            gr.Markdown(label="Validation Results")
        ]
        
        return validate_parameters, input_components, output_components