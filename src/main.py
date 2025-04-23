#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
Main entry point for the Quantum UI with Hugging Face integration.
Initializes and serves the Gradio interface.
"""

import os
import logging
import argparse
from typing import Dict, Any

import gradio as gr

from src.ui.layouts.main_layout import MainLayout
from src.core.services.huggingface import HuggingFaceService

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Quantum UI with Hugging Face Integration")
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0", 
        help="Host to serve the application"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=7860, 
        help="Port to serve the application"
    )
    parser.add_argument(
        "--share", 
        action="store_true", 
        help="Create a shareable link"
    )
    parser.add_argument(
        "--cache-dir", 
        type=str, 
        default=None, 
        help="Directory to cache Hugging Face models"
    )
    parser.add_argument(
        "--device", 
        type=str, 
        default=None, 
        help="Device to run models on ('cpu', 'cuda', etc.)"
    )
    
    return parser.parse_args()

def main() -> None:
    """Main entry point for the application."""
    # Parse command-line arguments
    args = parse_args()
    
    try:
        logger.info("Starting Quantum UI with Hugging Face integration")
        
        # Initialize Hugging Face service
        model_service = HuggingFaceService(
            cache_dir=args.cache_dir,
            device=args.device
        )
        logger.info(f"Initialized Hugging Face service with device: {model_service.get_device()}")
        
        # Create main layout
        main_layout = MainLayout(
            title="Quantum UI with Hugging Face Integration",
            description="A professional-grade quantum computing UI with integrated AI capabilities",
            theme="default",
            model_service=model_service
        )
        
        # Create and launch the interface
        interface = main_layout.create()
        interface.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            inbrowser=True
        )
        
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        raise

if __name__ == "__main__":
    main()