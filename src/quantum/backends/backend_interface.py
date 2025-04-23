#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
Quantum backend interface module.
Defines the abstract interface for all quantum backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import numpy as np


class QuantumBackend(ABC):
    """Abstract base class for quantum backends."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the backend service.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the backend service."""
        pass
    
    @abstractmethod
    def get_available_devices(self) -> List[Dict[str, Any]]:
        """Get list of available quantum devices.
        
        Returns:
            List of device information dictionaries
        """
        pass
    
    @abstractmethod
    def get_device_properties(self, device_id: str) -> Dict[str, Any]:
        """Get detailed properties of a specific device.
        
        Args:
            device_id: ID of the quantum device
            
        Returns:
            Dictionary of device properties
        """
        pass
    
    @abstractmethod
    def submit_circuit(self, 
                      circuit: Any, 
                      device_id: str, 
                      shots: int = 1024, 
                      optimization_level: int = 1) -> str:
        """Submit a quantum circuit for execution.
        
        Args:
            circuit: Quantum circuit to execute
            device_id: ID of the target quantum device
            shots: Number of measurement shots
            optimization_level: Circuit optimization level
            
        Returns:
            Job ID for the submitted job
        """
        pass
    
    @abstractmethod
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of a submitted job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary with job status information
        """
        pass
    
    @abstractmethod
    def get_job_results(self, job_id: str) -> Dict[str, Any]:
        """Get the results of a completed job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary with job results
        """
        pass
    
    @abstractmethod
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a submitted job.
        
        Args:
            job_id: ID of the job to cancel
            
        Returns:
            True if cancellation successful, False otherwise
        """
        pass
    
    @abstractmethod
    def transpile_circuit(self, 
                         circuit: Any, 
                         device_id: str,
                         optimization_level: int = 1) -> Any:
        """Transpile a circuit for a specific device.
        
        Args:
            circuit: Quantum circuit to transpile
            device_id: ID of the target quantum device
            optimization_level: Optimization level
            
        Returns:
            Transpiled circuit
        """
        pass