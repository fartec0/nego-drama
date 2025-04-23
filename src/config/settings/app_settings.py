#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Application settings for the Quantum UI."""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AppSettings:
    """Application settings for the Quantum UI."""
    
    # App configuration
    app_name: str = "Quantum UI"
    debug_mode: bool = False
    theme: str = "default"
    
    # Quantum simulation settings
    max_qubits: int = 10
    default_shots: int = 1024
    available_backends: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values for complex types."""
        if self.available_backends is None:
            self.available_backends = {
                "local_simulator": {
                    "name": "Local Simulator",
                    "description": "Local quantum circuit simulator",
                    "max_qubits": 20,
                },
                "qiskit_aer": {
                    "name": "Qiskit Aer",
                    "description": "Qiskit's Aer simulator",
                    "max_qubits": 30,
                },
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "app_name": self.app_name,
            "debug_mode": self.debug_mode,
            "theme": self.theme,
            "max_qubits": self.max_qubits,
            "default_shots": self.default_shots,
            "available_backends": self.available_backends,
        }