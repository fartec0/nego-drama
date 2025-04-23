#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hugging Face Text Generation component for Gradio UI.
This component provides a reusable text generation interface.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union, Callable

import gradio as gr

from src.core.services.huggingface.model_service import HuggingFaceService
from src.ui.integrations.huggingface.integration import HuggingFaceIntegration

class TextGenerationComponent:
    """Reusable Text Generation UI component based on Hugging Face models."""
    
    def __init__(
        self,
        model_name: str = "gpt2",
        title: str = "Text Generation",
        description: str = "Generate text using a language model",
        theme: str = "default",
        max_length: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        examples: List[List[Any]] = None,
        model_service: Optional[HuggingFaceService] = None
    ):
        """Initialize the Text Generation component.
        
        Args:
            model_name: Name of the Hugging Face model to use
            title: Title of the Gradio interface
            description: Description of the Gradio interface
            theme: Theme for the Gradio interface
            max_length: Default maximum length of generated text
            temperature: Default sampling temperature
            top_p: Default top-p sampling parameter
            examples: Example inputs for the interface
            model_service: Hugging Face model service instance
        """
        self.model_name = model_name
        self.title = title
        self.description = description
        self.theme = theme
        self.max_length = max_length
        self.temperature = temperature
        self.top_p = top_p
        self.examples = examples or []
        self.logger = logging.getLogger(__name__)
        
        # Create HuggingFace integration
        self.integration = HuggingFaceIntegration(model_service)
        
    def create(self) -> gr.Interface:
        """Create and return a Gradio interface for text generation.
        
        Returns:
            Gradio Interface object
        """
        self.logger.info(f"Creating Text Generation interface with model: {self.model_name}")
        
        try:
            # Get text generation interface components
            fn, inputs, outputs = self.integration.create_text_generation_interface(
                model_name=self.model_name,
                max_length=self.max_length,
                temperature=self.temperature,
                top_p=self.top_p
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
            self.logger.error(f"Failed to create Text Generation interface: {str(e)}")
            raise
            
    def as_tab(self) -> Tuple[str, gr.Blocks]:
        """Return the component as a tab for inclusion in a TabularInterface.
        
        Returns:
            Tuple of (tab_name, blocks_component)
        """
        fn, inputs, outputs = self.integration.create_text_generation_interface(
            model_name=self.model_name,
            max_length=self.max_length,
            temperature=self.temperature,
            top_p=self.top_p
        )
        
        with gr.Blocks() as block:
            with gr.Row():
                with gr.Column():
                    input_components = []
                    # Create input components
                    prompt = gr.Textbox(lines=5, label="Prompt")
                    max_len = gr.Slider(
                        minimum=1, maximum=500, value=self.max_length, 
                        step=1, label="Max Length"
                    )
                    temp = gr.Slider(
                        minimum=0.0, maximum=2.0, value=self.temperature, 
                        step=0.1, label="Temperature"
                    )
                    top_p_val = gr.Slider(
                        minimum=0.1, maximum=1.0, value=self.top_p, 
                        step=0.05, label="Top-p"
                    )
                    seed = gr.Number(label="Seed (optional)", precision=0)
                    input_components = [prompt, max_len, temp, top_p_val, seed]
                    
                    # Create output component
                    generated_text = gr.Textbox(lines=10, label="Generated Text")
                    
                    # Add examples if provided
                    if self.examples:
                        gr.Examples(
                            examples=self.examples,
                            inputs=input_components
                        )
                    
                    # Add submit button
                    submit_btn = gr.Button("Generate")
                    submit_btn.click(
                        fn=fn,
                        inputs=input_components,
                        outputs=generated_text
                    )
        
        return self.title, block