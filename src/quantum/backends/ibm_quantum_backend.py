#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IBM Quantum backend implementation.
Provides connection to IBM Quantum Experience devices.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Union
import numpy as np

try:
    from qiskit import IBMQ, Aer, transpile, assemble
    from qiskit.providers.ibmq import IBMQFactory, IBMQBackend, IBMQJob
    from qiskit.providers.ibmq.accountprovider import AccountProvider
except ImportError:
    logging.warning("Qiskit not installed. IBM Quantum backend will not be available.")

from src.quantum.backends.backend_interface import QuantumBackend
from src.core.interfaces.credentials_manager import CredentialsManager


class IBMQuantumBackend(QuantumBackend):
    """IBM Quantum Experience backend connector."""
    
    def __init__(self, credentials_manager: Optional[CredentialsManager] = None):
        """Initialize the IBM Quantum backend.
        
        Args:
            credentials_manager: Credentials manager for secure API token storage
        """
        self.credentials_manager = credentials_manager
        self.provider = None
        self.is_connected = False
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Connect to IBM Quantum Experience.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # First check if already loaded
            providers = IBMQ.providers()
            if providers:
                self.provider = providers[0]
                self.is_connected = True
                self.logger.info("Connected to existing IBM Quantum provider")
                return True
                
            # Get API token from credentials manager or environment
            if self.credentials_manager:
                token = self.credentials_manager.get_credential("ibmq_token")
            else:
                # This is a fallback and not recommended for production
                import os
                token = os.environ.get("IBMQ_TOKEN")
                
            if not token:
                self.logger.error("No IBM Quantum token available")
                return False
                
            # Load account and get provider
            IBMQ.save_account(token, overwrite=True)
            IBMQ.load_account()
            self.provider = IBMQ.providers()[0]
            self.is_connected = True
            self.logger.info("Successfully connected to IBM Quantum")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to IBM Quantum: {str(e)}")
            self.is_connected = False
            return False
            
    def disconnect(self) -> None:
        """Disconnect from IBM Quantum Experience."""
        try:
            IBMQ.disable_account()
            self.provider = None
            self.is_connected = False
            self.logger.info("Disconnected from IBM Quantum")
        except Exception as e:
            self.logger.error(f"Error during disconnection: {str(e)}")
            
    def get_available_devices(self) -> List[Dict[str, Any]]:
        """Get list of available IBM Quantum devices.
        
        Returns:
            List of device information dictionaries
        """
        if not self.is_connected:
            self.logger.warning("Not connected to IBM Quantum. Trying to connect...")
            if not self.connect():
                return []
                
        try:
            backends = self.provider.backends()
            devices = []
            
            for backend in backends:
                # Skip local simulators
                if backend.configuration().simulator:
                    continue
                    
                # Get basic info
                config = backend.configuration().to_dict()
                status = backend.status().to_dict()
                
                devices.append({
                    "id": backend.name(),
                    "name": config.get("backend_name", "Unknown"),
                    "version": config.get("backend_version", "Unknown"),
                    "n_qubits": config.get("n_qubits", 0),
                    "status": status.get("status", "unknown"),
                    "pending_jobs": status.get("pending_jobs", 0),
                    "is_operational": status.get("operational", False),
                    "max_shots": config.get("max_shots", 1000),
                    "basis_gates": config.get("basis_gates", []),
                })
                
            return devices
            
        except Exception as e:
            self.logger.error(f"Error getting available devices: {str(e)}")
            return []
            
    def get_device_properties(self, device_id: str) -> Dict[str, Any]:
        """Get detailed properties of a specific IBM Quantum device.
        
        Args:
            device_id: ID of the quantum device
            
        Returns:
            Dictionary of device properties
        """
        if not self.is_connected:
            self.logger.warning("Not connected to IBM Quantum. Trying to connect...")
            if not self.connect():
                return {}
                
        try:
            backend = self.provider.get_backend(device_id)
            config = backend.configuration().to_dict()
            props = backend.properties().to_dict() if hasattr(backend, "properties") else {}
            
            # Prepare properties dictionary
            properties = {
                "id": device_id,
                "name": config.get("backend_name", "Unknown"),
                "version": config.get("backend_version", "Unknown"),
                "n_qubits": config.get("n_qubits", 0),
                "basis_gates": config.get("basis_gates", []),
                "coupling_map": config.get("coupling_map", []),
                "max_shots": config.get("max_shots", 1000),
                "max_experiments": config.get("max_experiments", 1),
                "simulator": config.get("simulator", False),
                "local": config.get("local", False),
                "memory": config.get("memory", False),
                "online_date": config.get("online_date", "Unknown"),
                "gates": [],
                "qubits": []
            }
            
            # Add gate information
            if "gates" in props:
                properties["gates"] = props["gates"]
                
            # Add qubit information
            if "qubits" in props:
                properties["qubits"] = []
                for qubit, qubit_props in enumerate(props["qubits"]):
                    qubit_data = {"id": qubit, "properties": {}}
                    for prop in qubit_props:
                        name = prop.get("name", "unknown")
                        value = prop.get("value", 0)
                        unit = prop.get("unit", "")
                        qubit_data["properties"][name] = {"value": value, "unit": unit}
                    properties["qubits"].append(qubit_data)
            
            return properties
            
        except Exception as e:
            self.logger.error(f"Error getting device properties: {str(e)}")
            return {}
    
    def submit_circuit(self, 
                      circuit: Any, 
                      device_id: str, 
                      shots: int = 1024, 
                      optimization_level: int = 1) -> str:
        """Submit a quantum circuit to IBM Quantum.
        
        Args:
            circuit: Qiskit QuantumCircuit to execute
            device_id: ID of the target quantum device
            shots: Number of measurement shots
            optimization_level: Circuit optimization level
            
        Returns:
            Job ID for the submitted job
        """
        if not self.is_connected:
            self.logger.warning("Not connected to IBM Quantum. Trying to connect...")
            if not self.connect():
                return ""
                
        try:
            # Get backend
            backend = self.provider.get_backend(device_id)
            
            # Transpile the circuit for the backend
            transpiled_circuit = transpile(circuit, 
                                         backend=backend, 
                                         optimization_level=optimization_level)
            
            # Assemble the circuit into a qobj
            qobj = assemble(transpiled_circuit, backend=backend, shots=shots)
            
            # Submit the job
            job = backend.run(qobj)
            
            self.logger.info(f"Submitted job {job.job_id()} to {device_id}")
            return job.job_id()
            
        except Exception as e:
            self.logger.error(f"Error submitting circuit: {str(e)}")
            return ""
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get the status of a submitted job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary with job status information
        """
        if not self.is_connected:
            self.logger.warning("Not connected to IBM Quantum. Trying to connect...")
            if not self.connect():
                return {"status": "ERROR", "detail": "Not connected to IBM Quantum"}
                
        try:
            # Get the job
            job = self.provider.backends.retrieve_job(job_id)
            
            # Get status information
            status = job.status().name
            queue_position = job.queue_position() if hasattr(job, "queue_position") else None
            creation_date = job.creation_date()
            
            return {
                "job_id": job_id,
                "status": status,
                "queue_position": queue_position,
                "creation_date": creation_date.isoformat() if creation_date else None,
                "device": job.backend().name(),
                "error_message": job.error_message() if hasattr(job, "error_message") else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting job status: {str(e)}")
            return {"status": "ERROR", "detail": str(e)}
    
    def get_job_results(self, job_id: str) -> Dict[str, Any]:
        """Get the results of a completed job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Dictionary with job results
        """
        if not self.is_connected:
            self.logger.warning("Not connected to IBM Quantum. Trying to connect...")
            if not self.connect():
                return {"success": False, "error": "Not connected to IBM Quantum"}
                
        try:
            # Get the job
            job = self.provider.backends.retrieve_job(job_id)
            
            # Check if job is completed
            status = job.status().name
            if status != "DONE":
                return {
                    "success": False,
                    "error": f"Job not completed. Current status: {status}"
                }
                
            # Get the results
            result = job.result()
            counts = result.get_counts()
            
            # Format the results
            if isinstance(counts, dict):
                # Single circuit result
                formatted_counts = counts
            else:
                # Multiple circuit results
                formatted_counts = {f"circuit_{i}": count for i, count in enumerate(counts)}
            
            return {
                "success": True,
                "job_id": job_id,
                "device": job.backend().name(),
                "status": status,
                "counts": formatted_counts,
                "execution_time": result.time_taken if hasattr(result, "time_taken") else None,
                "metadata": result.to_dict().get("results", [{}])[0].get("header", {})
            }
            
        except Exception as e:
            self.logger.error(f"Error getting job results: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a submitted job.
        
        Args:
            job_id: ID of the job to cancel
            
        Returns:
            True if cancellation successful, False otherwise
        """
        if not self.is_connected:
            self.logger.warning("Not connected to IBM Quantum. Trying to connect...")
            if not self.connect():
                return False
                
        try:
            # Get the job
            job = self.provider.backends.retrieve_job(job_id)
            
            # Cancel the job
            result = job.cancel()
            
            if result:
                self.logger.info(f"Successfully canceled job {job_id}")
            else:
                self.logger.warning(f"Failed to cancel job {job_id}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error canceling job: {str(e)}")
            return False
    
    def transpile_circuit(self, 
                         circuit: Any, 
                         device_id: str,
                         optimization_level: int = 1) -> Any:
        """Transpile a circuit for a specific IBM Quantum device.
        
        Args:
            circuit: Qiskit QuantumCircuit to transpile
            device_id: ID of the target quantum device
            optimization_level: Optimization level
            
        Returns:
            Transpiled circuit
        """
        if not self.is_connected:
            self.logger.warning("Not connected to IBM Quantum. Trying to connect...")
            if not self.connect():
                return None
                
        try:
            # Get backend
            backend = self.provider.get_backend(device_id)
            
            # Transpile the circuit
            transpiled_circuit = transpile(circuit, 
                                         backend=backend, 
                                         optimization_level=optimization_level)
            
            return transpiled_circuit
            
        except Exception as e:
            self.logger.error(f"Error transpiling circuit: {str(e)}")
            return None