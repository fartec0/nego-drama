"""
AIF360 Integration Module for Quantum Applications

This module serves as the integration layer between the AIF360 service
and the UI components, handling the data flow and business logic.
"""

import logging
from typing import Dict, List, Any, Union, Optional

import numpy as np
import pandas as pd

from src.core.services.aif360 import AIF360Service

logger = logging.getLogger(__name__)

class AIF360Integration:
    """
    Integration layer for the AIF360 fairness service.
    
    This class handles:
    1. Preparing data for fairness analysis
    2. Converting between UI and service formats
    3. Coordinating fairness operations across quantum algorithms
    """
    
    def __init__(self):
        """Initialize the AIF360 integration."""
        logger.info("Initializing AIF360 integration layer")
        self.service = AIF360Service()
        self.last_metrics = {}
        
    def analyze_fairness(self, 
                       data: pd.DataFrame,
                       label_column: str,
                       protected_attributes: List[str],
                       privileged_groups: List[Dict[str, Any]],
                       unprivileged_groups: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Analyze fairness metrics for a quantum algorithm output.
        
        Args:
            data: DataFrame containing algorithm outputs
            label_column: Column name for outcome labels
            protected_attributes: Column names for protected attributes
            privileged_groups: List of dicts defining privileged groups
            unprivileged_groups: List of dicts defining unprivileged groups
            
        Returns:
            Dict of fairness metrics
        """
        logger.info(f"Analyzing fairness for {len(data)} samples with protected attributes: {protected_attributes}")
        
        # Prepare dataset for analysis
        dataset = self.service.prepare_dataset(
            data=data,
            label_column=label_column,
            protected_attributes=protected_attributes
        )
        
        # Compute bias metrics
        metrics = self.service.compute_bias_metrics(
            dataset=dataset,
            privileged_groups=privileged_groups,
            unprivileged_groups=unprivileged_groups
        )
        
        self.last_metrics = metrics
        return metrics
    
    def apply_mitigation(self,
                       data: pd.DataFrame,
                       label_column: str,
                       protected_attributes: List[str],
                       privileged_groups: List[Dict[str, Any]],
                       unprivileged_groups: List[Dict[str, Any]],
                       method: str = 'reweighing') -> pd.DataFrame:
        """
        Apply fairness mitigation to quantum algorithm outputs.
        
        Args:
            data: DataFrame containing algorithm outputs
            label_column: Column name for outcome labels
            protected_attributes: Column names for protected attributes
            privileged_groups: List of dicts defining privileged groups
            unprivileged_groups: List of dicts defining unprivileged groups
            method: Mitigation method to apply
            
        Returns:
            DataFrame with bias mitigation applied
        """
        logger.info(f"Applying {method} mitigation to quantum algorithm outputs")
        
        # Prepare dataset for mitigation
        dataset = self.service.prepare_dataset(
            data=data,
            label_column=label_column,
            protected_attributes=protected_attributes
        )
        
        # Apply mitigation
        transformed_dataset = self.service.mitigate_bias(
            dataset=dataset,
            privileged_groups=privileged_groups,
            unprivileged_groups=unprivileged_groups,
            method=method
        )
        
        # Convert back to DataFrame
        mitigated_df = transformed_dataset.convert_to_dataframe()[0]
        logger.debug(f"Mitigation complete, returning dataframe with shape {mitigated_df.shape}")
        
        return mitigated_df
    
    def audit_grovers_search(self,
                           data: pd.DataFrame,
                           protected_attribute: str,
                           search_results: List[Any],
                           favorable_outcomes: List[Any]) -> Dict[str, float]:
        """
        Audit Grover's algorithm search results for fairness.
        
        Args:
            data: Original dataset the algorithm searched
            protected_attribute: Name of protected attribute column
            search_results: Results from Grover's algorithm
            favorable_outcomes: List of outcomes considered favorable
            
        Returns:
            Dict of fairness metrics for the search results
        """
        logger.info(f"Auditing Grover's algorithm with protected attribute: {protected_attribute}")
        
        metrics = self.service.audit_grovers_algorithm(
            dataset=data,
            protected_attribute=protected_attribute,
            search_results=search_results,
            favorable_outcomes=favorable_outcomes
        )
        
        return metrics
    
    def analyze_quantum_nn(self,
                         predictions: np.ndarray,
                         actual_labels: np.ndarray,
                         protected_attributes: np.ndarray,
                         protected_attribute_names: List[str],
                         privileged_values: List[Union[int, float, str]]):
        """
        Analyze fairness of quantum neural network predictions.
        
        Args:
            predictions: Model predictions
            actual_labels: Ground truth labels
            protected_attributes: Values of protected attributes
            protected_attribute_names: Names of protected attributes
            privileged_values: Values considered privileged for each attribute
            
        Returns:
            Dict of fairness metrics for QNN predictions
        """
        logger.info("Analyzing quantum neural network fairness")
        
        if len(protected_attribute_names) != protected_attributes.shape[1]:
            raise ValueError("Number of protected attribute names must match the shape of protected_attributes")
            
        # Prepare privileged and unprivileged groups
        privileged_groups = []
        unprivileged_groups = []
        
        for i, attr_name in enumerate(protected_attribute_names):
            priv_value = privileged_values[i]
            
            # Create group definitions
            privileged_groups.append({attr_name: priv_value})
            
            # Find other values for unprivileged groups
            unique_values = np.unique(protected_attributes[:, i])
            for val in unique_values:
                if val != priv_value:
                    unprivileged_groups.append({attr_name: val})
        
        # Analyze fairness
        metrics = self.service.analyze_qnn_fairness(
            predictions=predictions,
            actual_labels=actual_labels,
            protected_attributes=protected_attributes,
            privileged_groups=privileged_groups,
            unprivileged_groups=unprivileged_groups
        )
        
        return metrics