#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main entry point for the Quantum UI application.
This module initializes and runs the Gradio-based quantum computing interface.
"""

import gradio as gr
from src.ui.components.circuit_builder import CircuitBuilderComponent
from src.ui.components.state_visualizer import StateVisualizerComponent
from src.ui.layouts.main_layout import create_main_layout
from src.config.settings.app_settings import AppSettings

def initialize_app():
    """Initialize the Quantum UI application."""
    settings = AppSettings()
    return create_main_layout(settings)

def main():
    """Run the Quantum UI application."""
    app = initialize_app()
    app.launch(share=False, server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main()