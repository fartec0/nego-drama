#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hugging Face Image Classification component for Gradio UI.
This component provides a reusable image classification interface.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union, Callable, Tuple

import gradio as gr

from src.core.services.huggingface.model_service import HuggingFaceService
from src.ui.integrations.huggingface.integration import HuggingFaceIntegration

class ImageClassificationComponent:
    """Reusable Image Classification UI component based on Hugging Face models."""
    
    def __init__(
        self,
        model_name: str = "microsoft/resnet-50",
        title: str = "Image Classification",
        description: str = "Classify images using computer vision",
        theme: str = "default",
        examples: List[List[Any]] = None,
        model_service: Optional[HuggingFaceService] = None
    ):
        """Initialize the Image Classification component.
        
        Args:
            model_name: Name of the Hugging Face model to use
            title: Title of the Gradio interface
            description: Description of the Gradio interface
            theme: Theme for the Gradio interface
            examples: Example inputs for the interface
            model_service: Hugging Face model service instance
        """
        self.model_name = model_name
        self.title = title
        self.description = description
        self.theme = theme
        self.examples = examples or []
        self.logger = logging.getLogger(__name__)
        
        # Create HuggingFace integration
        self.integration = HuggingFaceIntegration(model_service)
        
    def create(self) -> gr.Interface:
        """Create and return a Gradio interface for image classification.
        
        Returns:
            Gradio Interface object
        """
        self.logger.info(f"Creating Image Classification interface with model: {self.model_name}")
        
        try:
            # Get image classification interface components
            fn, inputs, outputs = self.integration.create_image_classification_interface(
                model_name=self.model_name
            )
            
            # Create Gradio interface
            interface = gr.Interface(
                fn=fn,
                inputs=inputs,
                outputs=outputs,
                title=self.title,
                description=self.description,
                theme=self.theme,
                examples=self.examples,
                allow_flagging="never"
            )
            
            return interface
            
        except Exception as e:
            self.logger.error(f"Failed to create Image Classification interface: {str(e)}")
            raise
            
    def as_tab(self) -> Tuple[str, gr.Blocks]:
        """Return the component as a tab for inclusion in a TabularInterface.
        
        Returns:
            Tuple of (tab_name, blocks_component)
        """
        fn, inputs, outputs = self.integration.create_image_classification_interface(
            model_name=self.model_name
        )
        
        with gr.Blocks() as block:
            with gr.Row():
                with gr.Column(scale=1):
                    input_image = gr.Image(type="pil", label="Upload Image")
                    
                    # Add examples if provided
                    if self.examples:
                        gr.Examples(
                            examples=self.examples,
                            inputs=input_image
                        )
                    
                    # Add submit button
                    submit_btn = gr.Button("Classify")
                
                with gr.Column(scale=1):
                    output_label = gr.Label(label="Classification Results")
                    
                    submit_btn.click(
                        fn=fn,
                        inputs=input_image,
                        outputs=output_label
                    )
        
        return self.title, block