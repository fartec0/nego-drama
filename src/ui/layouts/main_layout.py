#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
Main layout for the Quantum UI with Hugging Face integration.
This module integrates quantum simulation components with Hugging Face AI models.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union

import gradio as gr

from src.ui.components.circuit_builder import QuantumCircuitComponent
from src.ui.components.state_visualizer import StateVisualizerComponent
from src.ui.components.huggingface import TextGenerationComponent, ImageClassificationComponent
from src.core.services.huggingface import HuggingFaceService

class MainLayout:
    """Main layout for the integrated Quantum UI with Hugging Face."""
    
    def __init__(
        self,
        title: str = "Quantum UI with Hugging Face Integration",
        description: str = "A professional-grade quantum computing UI with Hugging Face AI models",
        theme: str = "default",
        model_service: Optional[HuggingFaceService] = None
    ):
        """Initialize the main layout.
        
        Args:
            title: Title for the UI
            description: Description for the UI
            theme: Theme for the UI
            model_service: Hugging Face model service instance
        """
        self.title = title
        self.description = description
        self.theme = theme
        self.logger = logging.getLogger(__name__)
        self.model_service = model_service or HuggingFaceService()
        
    def create(self) -> gr.Blocks:
        """Create and return the main Gradio interface.
        
        Returns:
            Gradio Blocks interface
        """
        self.logger.info("Creating main Gradio interface")
        
        # Initialize components
        circuit_builder = QuantumCircuitComponent()
        state_visualizer = StateVisualizerComponent() 
        text_generator = TextGenerationComponent(
            model_name="gpt2",
            title="Text Generation",
            model_service=self.model_service
        )
        image_classifier = ImageClassificationComponent(
            model_name="microsoft/resnet-50",
            title="Image Classification",
            model_service=self.model_service
        )
        
        # Create the main interface with tabs
        with gr.Blocks(title=self.title, theme=self.theme) as interface:
            gr.Markdown(f"# {self.title}")
            gr.Markdown(self.description)
            
            with gr.Tabs():
                with gr.Tab("Quantum Simulation"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            # Quantum Circuit Builder
                            circuit_component = circuit_builder.create_component()
                        
                        with gr.Column(scale=1):
                            # Quantum State Visualizer
                            state_component = state_visualizer.create_component()
                
                with gr.Tab("Text Generation"):
                    # Get text generation component as blocks
                    _, text_gen_block = text_generator.as_tab()
                    text_gen_block.render()
                
                with gr.Tab("Image Classification"):
                    # Get image classification component as blocks
                    _, img_class_block = image_classifier.as_tab()
                    img_class_block.render()
            
            gr.Markdown("""
            ## About this Application
            
            This application integrates quantum computing simulation with AI capabilities:
            
            - **Quantum Simulation**: Design quantum circuits and visualize quantum states
            - **Text Generation**: Generate text using Hugging Face language models
            - **Image Classification**: Classify images using computer vision models
            
            Built with Gradio 2.52.5 and Hugging Face Transformers.
            """)
        
        return interface