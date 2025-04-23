#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
DeepChecks service for quantum-specific data validation and model monitoring.
This service provides utilities for validating classical data inputs for quantum models,
monitoring quantum-enhanced ML models, and analyzing quantum circuit parameters.
"""

import os
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union, Tuple

import numpy as np
import pandas as pd
from deepchecks.tabular import Dataset, Suite, Check
from deepchecks.tabular.checks import MultivariateDrift, DataDuplicates
from deepchecks.utils.html import create_html_report

class DeepChecksService:
    """Service for integrating DeepChecks validation with quantum workflows."""
    
    def __init__(self):
        """Initialize the DeepChecks service."""
        self.logger = logging.getLogger(__name__)
        self._temp_dir = tempfile.mkdtemp(prefix="deepchecks_")
        
    def create_tabular_dataset(
        self, 
        df: pd.DataFrame, 
        label_name: Optional[str] = None,
        cat_features: Optional[List[str]] = None,
        dataset_name: str = "Dataset"
    ) -> Dataset:
        """Create a DeepChecks tabular dataset from a pandas DataFrame.
        
        Args:
            df: Input DataFrame
            label_name: Name of the column containing labels
            cat_features: List of categorical feature names
            dataset_name: Name for the dataset
            
        Returns:
            DeepChecks Dataset object
        """
        self.logger.info(f"Creating tabular dataset '{dataset_name}' with shape {df.shape}")
        
        try:
            return Dataset(
                df=df,
                label=label_name,
                cat_features=cat_features,
                name=dataset_name
            )
        except Exception as e:
            self.logger.error(f"Error creating dataset: {str(e)}")
            raise
            
    def validate_quantum_input_data(
        self, 
        dataset: Dataset,
        checks: Optional[List[Check]] = None
    ) -> Any:
        """Validate classical data inputs for quantum models.
        
        Args:
            dataset: DeepChecks dataset to validate
            checks: List of DeepChecks checks to run
            
        Returns:
            DeepChecks validation result
        """
        self.logger.info("Validating quantum input data")
        
        # Default checks for quantum input data
        if checks is None:
            checks = [
                DataDuplicates(),
                MultivariateDrift()
            ]
        
        # Create a validation suite
        suite = Suite("Quantum Input Data Validation")
        for check in checks:
            suite.add(check)
            
        # Run the validation
        try:
            result = suite.run(dataset)
            return result
        except Exception as e:
            self.logger.error(f"Error validating data: {str(e)}")
            raise
            
    def check_dataset_drift(
        self,
        reference_dataset: Dataset,
        current_dataset: Dataset,
        drift_threshold: float = 0.05
    ) -> Any:
        """Check for drift between reference and current datasets.
        
        Args:
            reference_dataset: Reference dataset (training data)
            current_dataset: Current dataset (production data)
            drift_threshold: Threshold for drift detection
            
        Returns:
            DeepChecks drift checking result
        """
        self.logger.info("Checking for dataset drift")
        
        # Create a drift suite
        suite = Suite("Quantum Model Drift Check")
        suite.add(MultivariateDrift(threshold=drift_threshold))
        
        # Run the drift check
        try:
            result = suite.run(reference_dataset, current_dataset)
            return result
        except Exception as e:
            self.logger.error(f"Error checking drift: {str(e)}")
            raise
            
    def generate_html_report(
        self,
        result: Any,
        output_path: Optional[str] = None
    ) -> str:
        """Generate an HTML report from DeepChecks results.
        
        Args:
            result: DeepChecks result object
            output_path: Path to save the HTML report
            
        Returns:
            Path to the generated HTML report
        """
        if output_path is None:
            output_path = os.path.join(self._temp_dir, "deepchecks_report.html")
            
        self.logger.info(f"Generating HTML report at {output_path}")
        
        try:
            create_html_report(result, output_path)
            return output_path
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise
            
    def detect_parameter_anomalies(
        self,
        parameters: np.ndarray,
        parameter_names: List[str],
        threshold: float = 3.0
    ) -> Dict[str, bool]:
        """Detect anomalies in quantum circuit parameters.
        
        This function uses z-score to detect outliers in quantum circuit parameters.
        
        Args:
            parameters: Array of parameter values
            parameter_names: Names of parameters
            threshold: Z-score threshold for anomaly detection
            
        Returns:
            Dictionary mapping parameter names to anomaly flags
        """
        self.logger.info(f"Detecting parameter anomalies with threshold {threshold}")
        
        if len(parameters) != len(parameter_names):
            raise ValueError("Number of parameters must match number of parameter names")
            
        # Calculate z-scores
        mean = np.mean(parameters)
        std = np.std(parameters)
        z_scores = np.abs((parameters - mean) / (std + 1e-10))
        
        # Detect anomalies
        anomalies = {}
        for i, name in enumerate(parameter_names):
            is_anomaly = z_scores[i] > threshold
            anomalies[name] = is_anomaly
            if is_anomaly:
                self.logger.warning(f"Anomaly detected in parameter '{name}': {parameters[i]} (z-score: {z_scores[i]:.2f})")
                
        return anomalies
        
    def validate_quantum_circuit_parameters(
        self,
        parameters: Dict[str, float],
        param_constraints: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> Dict[str, Any]:
        """Validate quantum circuit parameters against constraints.
        
        Args:
            parameters: Dictionary mapping parameter names to values
            param_constraints: Dictionary mapping parameter names to (min, max) ranges
            
        Returns:
            Dictionary with validation results
        """
        self.logger.info("Validating quantum circuit parameters")
        
        if param_constraints is None:
            # Default constraints for common quantum parameters
            param_constraints = {
                "angle": (0, 2 * np.pi),         # Rotation angles should be 0-2π
                "depth": (1, 100),               # Circuit depth reasonable range
                "entanglement": (0, 1.0),        # Entanglement parameters typically 0-1
                "amplitude": (-1.0, 1.0)         # Amplitude parameters typically -1 to 1
            }
            
        results = {
            "valid": True,
            "violations": []
        }
        
        for name, value in parameters.items():
            # Find matching constraint (exact or by prefix)
            constraint = None
            for constraint_key, constraint_range in param_constraints.items():
                if name == constraint_key or name.startswith(constraint_key):
                    constraint = constraint_range
                    break
                    
            if constraint is not None:
                min_val, max_val = constraint
                if value < min_val or value > max_val:
                    results["valid"] = False
                    results["violations"].append({
                        "parameter": name,
                        "value": value,
                        "expected_range": (min_val, max_val),
                        "message": f"Parameter '{name}' with value {value} is outside " +
                                   f"expected range [{min_val}, {max_val}]"
                    })
                    self.logger.warning(f"Parameter '{name}' with value {value} is outside expected range [{min_val}, {max_val}]")
        
        return results