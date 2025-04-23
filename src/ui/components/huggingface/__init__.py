"""
Hugging Face UI components for Gradio.
"""

from src.ui.components.huggingface.text_generation import TextGenerationComponent
from src.ui.components.huggingface.image_classification import ImageClassificationComponent

__all__ = [
    'TextGenerationComponent',
    'ImageClassificationComponent',
]