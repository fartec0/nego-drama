#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hugging Face integration for Gradio UI components.
Provides utility functions for connecting Hugging Face models to Gradio interfaces.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union, Callable, Tuple

import gradio as gr
import numpy as np
from PIL import Image

from src.core.services.huggingface.model_service import HuggingFaceService

class HuggingFaceIntegration:
    """Integration layer between Hugging Face models and Gradio UI."""
    
    def __init__(self, model_service: Optional[HuggingFaceService] = None):
        """Initialize the Hugging Face integration.
        
        Args:
            model_service: Hugging Face model service instance
        """
        self.model_service = model_service or HuggingFaceService()
        self.logger = logging.getLogger(__name__)
        
    def create_text_generation_interface(
        self, 
        model_name: str = "gpt2", 
        max_length: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **model_kwargs
    ) -> Tuple[Callable, List[gr.components.Component], List[gr.components.Component]]:
        """Create a Gradio interface for text generation.
        
        Args:
            model_name: Name of the Hugging Face model to use
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **model_kwargs: Additional model parameters
            
        Returns:
            Tuple of (inference function, input components, output components)
        """
        self.logger.info(f"Creating text generation interface with model: {model_name}")
        
        try:
            # Load model and tokenizer
            tokenizer = self.model_service.load_tokenizer(model_name)
            model = self.model_service.load_model(model_name, "text-generation")
            
            # Define inference function
            def generate_text(
                prompt: str, 
                max_new_tokens: int = max_length,
                temp: float = temperature,
                top_p_val: float = top_p,
                seed: int = None
            ) -> str:
                try:
                    # Set seed for reproducibility if provided
                    if seed is not None:
                        import torch
                        torch.manual_seed(seed)
                        
                    # Prepare inputs
                    inputs = tokenizer(prompt, return_tensors="pt").to(self.model_service.get_device())
                    
                    # Generate text
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        temperature=temp,
                        top_p=top_p_val,
                        do_sample=temp > 0,
                        pad_token_id=tokenizer.eos_token_id
                    )
                    
                    # Decode and return the generated text
                    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    return generated_text
                    
                except Exception as e:
                    self.logger.error(f"Text generation error: {str(e)}")
                    return f"Error generating text: {str(e)}"
            
            # Define Gradio components
            input_components = [
                gr.Textbox(lines=5, label="Prompt"),
                gr.Slider(minimum=1, maximum=500, value=max_length, step=1, label="Max Length"),
                gr.Slider(minimum=0.0, maximum=2.0, value=temperature, step=0.1, label="Temperature"),
                gr.Slider(minimum=0.1, maximum=1.0, value=top_p, step=0.05, label="Top-p"),
                gr.Number(label="Seed (optional)", precision=0)
            ]
            
            output_components = [
                gr.Textbox(lines=10, label="Generated Text")
            ]
            
            return generate_text, input_components, output_components
            
        except Exception as e:
            self.logger.error(f"Failed to create text generation interface: {str(e)}")
            raise
            
    def create_image_classification_interface(
        self,
        model_name: str = "microsoft/resnet-50",
        **model_kwargs
    ) -> Tuple[Callable, List[gr.components.Component], List[gr.components.Component]]:
        """Create a Gradio interface for image classification.
        
        Args:
            model_name: Name of the Hugging Face model to use
            **model_kwargs: Additional model parameters
            
        Returns:
            Tuple of (inference function, input components, output components)
        """
        self.logger.info(f"Creating image classification interface with model: {model_name}")
        
        try:
            # Create pipeline
            classifier = self.model_service.create_pipeline(
                task="image-classification",
                model_name=model_name,
                **model_kwargs
            )
            
            # Define inference function
            def classify_image(image: Union[np.ndarray, Image.Image]) -> Dict[str, float]:
                try:
                    # Ensure image is a PIL Image
                    if isinstance(image, np.ndarray):
                        image = Image.fromarray(image)
                        
                    # Run classification
                    results = classifier(image)
                    
                    # Convert to dictionary format for Gradio Label component
                    return {result["label"]: result["score"] for result in results}
                    
                except Exception as e:
                    self.logger.error(f"Image classification error: {str(e)}")
                    return {"error": 1.0}
            
            # Define Gradio components
            input_components = [
                gr.Image(type="pil", label="Upload Image")
            ]
            
            output_components = [
                gr.Label(label="Classification Results")
            ]
            
            return classify_image, input_components, output_components
            
        except Exception as e:
            self.logger.error(f"Failed to create image classification interface: {str(e)}")
            raise
            
    def create_text_translation_interface(
        self,
        model_name: str = "Helsinki-NLP/opus-mt-en-fr",
        **model_kwargs
    ) -> Tuple[Callable, List[gr.components.Component], List[gr.components.Component]]:
        """Create a Gradio interface for text translation.
        
        Args:
            model_name: Name of the Hugging Face model to use
            **model_kwargs: Additional model parameters
            
        Returns:
            Tuple of (inference function, input components, output components)
        """
        self.logger.info(f"Creating translation interface with model: {model_name}")
        
        try:
            # Create pipeline
            translator = self.model_service.create_pipeline(
                task="translation",
                model_name=model_name,
                **model_kwargs
            )
            
            # Define inference function
            def translate_text(text: str) -> str:
                try:
                    result = translator(text)
                    
                    if isinstance(result, list):
                        return result[0]["translation_text"]
                    return result["translation_text"]
                    
                except Exception as e:
                    self.logger.error(f"Translation error: {str(e)}")
                    return f"Error translating text: {str(e)}"
            
            # Define Gradio components
            input_components = [
                gr.Textbox(lines=5, label="Text to Translate")
            ]
            
            output_components = [
                gr.Textbox(lines=5, label="Translated Text")
            ]
            
            return translate_text, input_components, output_components
            
        except Exception as e:
            self.logger.error(f"Failed to create translation interface: {str(e)}")
            raise
            
    def create_text_summarization_interface(
        self,
        model_name: str = "facebook/bart-large-cnn",
        **model_kwargs
    ) -> Tuple[Callable, List[gr.components.Component], List[gr.components.Component]]:
        """Create a Gradio interface for text summarization.
        
        Args:
            model_name: Name of the Hugging Face model to use
            **model_kwargs: Additional model parameters
            
        Returns:
            Tuple of (inference function, input components, output components)
        """
        self.logger.info(f"Creating summarization interface with model: {model_name}")
        
        try:
            # Create pipeline
            summarizer = self.model_service.create_pipeline(
                task="summarization",
                model_name=model_name,
                **model_kwargs
            )
            
            # Define inference function
            def summarize_text(
                text: str,
                max_length: int = 130,
                min_length: int = 30
            ) -> str:
                try:
                    result = summarizer(
                        text, 
                        max_length=max_length, 
                        min_length=min_length, 
                        do_sample=False
                    )
                    
                    if isinstance(result, list):
                        return result[0]["summary_text"]
                    return result["summary_text"]
                    
                except Exception as e:
                    self.logger.error(f"Summarization error: {str(e)}")
                    return f"Error summarizing text: {str(e)}"
            
            # Define Gradio components
            input_components = [
                gr.Textbox(lines=10, label="Text to Summarize"),
                gr.Slider(minimum=10, maximum=500, value=130, step=10, label="Max Length"),
                gr.Slider(minimum=10, maximum=200, value=30, step=10, label="Min Length")
            ]
            
            output_components = [
                gr.Textbox(lines=5, label="Summary")
            ]
            
            return summarize_text, input_components, output_components
            
        except Exception as e:
            self.logger.error(f"Failed to create summarization interface: {str(e)}")
            raise