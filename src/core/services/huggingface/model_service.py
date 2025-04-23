#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
Hugging Face model service for managing models and tokenizers.
Provides a centralized interface for loading and using Hugging Face models.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union, Callable

import torch
from huggingface_hub import HfApi, HfFolder, Repository
from transformers import (
    AutoConfig, 
    AutoModel, 
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    AutoModelForSequenceClassification,
    AutoModelForImageClassification,
    AutoTokenizer,
    pipeline
)

class HuggingFaceService:
    """Service for managing Hugging Face models and tokenizers."""
    
    def __init__(self, cache_dir: Optional[str] = None, device: Optional[str] = None):
        """Initialize the Hugging Face service.
        
        Args:
            cache_dir: Directory to cache downloaded models
            device: Device to run models on ('cpu', 'cuda', 'mps', etc.)
        """
        self.cache_dir = cache_dir
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger = logging.getLogger(__name__)
        self.loaded_models = {}
        self.loaded_tokenizers = {}
        
    def load_model(
        self, 
        model_name: str, 
        task_type: str = "text-generation", 
        **model_kwargs
    ) -> Any:
        """Load a model from Hugging Face Hub.
        
        Args:
            model_name: Name or path of the model on Hugging Face Hub
            task_type: Type of task for the model
            **model_kwargs: Additional arguments for model loading
            
        Returns:
            Loaded model
        """
        # Check if model is already loaded
        model_key = f"{model_name}_{task_type}"
        if model_key in self.loaded_models:
            self.logger.info(f"Using cached model: {model_name}")
            return self.loaded_models[model_key]
            
        try:
            self.logger.info(f"Loading model: {model_name} for task: {task_type}")
            
            # Configure model loading based on task type
            if task_type == "text-generation":
                model = AutoModelForCausalLM.from_pretrained(
                    model_name, 
                    cache_dir=self.cache_dir,
                    torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                    **model_kwargs
                )
            elif task_type == "translation" or task_type == "summarization":
                model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name, 
                    cache_dir=self.cache_dir,
                    **model_kwargs
                )
            elif task_type == "text-classification":
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_name, 
                    cache_dir=self.cache_dir,
                    **model_kwargs
                )
            elif task_type == "image-classification":
                model = AutoModelForImageClassification.from_pretrained(
                    model_name, 
                    cache_dir=self.cache_dir,
                    **model_kwargs
                )
            else:
                # Default to base model for other tasks
                model = AutoModel.from_pretrained(
                    model_name, 
                    cache_dir=self.cache_dir,
                    **model_kwargs
                )
                
            # Move model to appropriate device
            model = model.to(self.device)
            
            # Cache the loaded model
            self.loaded_models[model_key] = model
            
            return model
            
        except Exception as e:
            self.logger.error(f"Error loading model {model_name}: {str(e)}")
            raise
            
    def load_tokenizer(self, model_name: str, **tokenizer_kwargs) -> Any:
        """Load a tokenizer from Hugging Face Hub.
        
        Args:
            model_name: Name or path of the model on Hugging Face Hub
            **tokenizer_kwargs: Additional arguments for tokenizer loading
            
        Returns:
            Loaded tokenizer
        """
        # Check if tokenizer is already loaded
        if model_name in self.loaded_tokenizers:
            self.logger.info(f"Using cached tokenizer: {model_name}")
            return self.loaded_tokenizers[model_name]
            
        try:
            self.logger.info(f"Loading tokenizer: {model_name}")
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                cache_dir=self.cache_dir,
                **tokenizer_kwargs
            )
            
            # Cache the loaded tokenizer
            self.loaded_tokenizers[model_name] = tokenizer
            
            return tokenizer
            
        except Exception as e:
            self.logger.error(f"Error loading tokenizer {model_name}: {str(e)}")
            raise
            
    def create_pipeline(
        self, 
        task: str, 
        model_name: str = None, 
        model = None, 
        tokenizer = None, 
        **pipeline_kwargs
    ) -> Callable:
        """Create a pipeline for a specific task.
        
        Args:
            task: Task name for the pipeline
            model_name: Name or path of the model on Hugging Face Hub
            model: Pre-loaded model (optional)
            tokenizer: Pre-loaded tokenizer (optional)
            **pipeline_kwargs: Additional arguments for pipeline configuration
            
        Returns:
            Pipeline function
        """
        try:
            self.logger.info(f"Creating pipeline for task: {task}")
            
            # If model and tokenizer are not provided but model_name is, load them
            if model is None and model_name is not None:
                model = self.load_model(model_name, task)
                
            if tokenizer is None and model_name is not None:
                tokenizer = self.load_tokenizer(model_name)
                
            # Create the pipeline
            pipe = pipeline(
                task=task,
                model=model,
                tokenizer=tokenizer,
                device=0 if self.device == 'cuda' else -1,
                **pipeline_kwargs
            )
            
            return pipe
            
        except Exception as e:
            self.logger.error(f"Error creating pipeline for task {task}: {str(e)}")
            raise
            
    def get_device(self) -> str:
        """Get the current device being used for inference.
        
        Returns:
            Device name
        """
        return self.device
        
    def set_device(self, device: str) -> None:
        """Set the device for inference.
        
        Args:
            device: Device name ('cpu', 'cuda', 'mps', etc.)
        """
        self.device = device
        self.logger.info(f"Set device to: {device}")
        
        # Move all loaded models to the new device
        for key, model in self.loaded_models.items():
            self.loaded_models[key] = model.to(device)
            
    def clear_cache(self) -> None:
        """Clear the cached models and tokenizers."""
        self.loaded_models = {}
        self.loaded_tokenizers = {}
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        self.logger.info("Cleared model and tokenizer cache")