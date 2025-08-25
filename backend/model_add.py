"""
Model adapter for LlamaCPP integration with Haystack
This file provides the LlamaCPPInvocationLayer class that was missing from the original project
"""

from typing import List, Dict, Any, Optional, Union
import logging
from pathlib import Path
import os

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None

try:
    from haystack.nodes.prompt.invocation_layer.base import BaseInvocationLayer
    from haystack.nodes.prompt.invocation_layer.handlers import DefaultPromptHandler
    HAYSTACK_AVAILABLE = True
except ImportError:
    HAYSTACK_AVAILABLE = False
    BaseInvocationLayer = object
    DefaultPromptHandler = object

logger = logging.getLogger(__name__)

class LlamaCPPInvocationLayer(BaseInvocationLayer if HAYSTACK_AVAILABLE else object):
    """
    Invocation layer for LlamaCPP models to work with Haystack PromptNode
    """
    
    def __init__(
        self,
        model_name_or_path: str,
        max_length: int = 512,
        max_tokens: int = 512,
        temperature: float = 0.1,
        top_p: float = 0.95,
        n_ctx: int = 2048,
        n_batch: int = 512,
        n_threads: Optional[int] = None,
        use_gpu: bool = False,
        **kwargs
    ):
        """
        Initialize LlamaCPP model
        
        Args:
            model_name_or_path: Path to the GGUF model file
            max_length: Maximum length of generated response
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            n_ctx: Context size
            n_batch: Batch size for processing
            n_threads: Number of CPU threads to use
            use_gpu: Whether to use GPU (if available)
        """
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError("llama-cpp-python is not installed. Please install it with: pip install llama-cpp-python")
        
        self.model_name_or_path = model_name_or_path
        self.max_length = max_length
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.n_ctx = n_ctx
        self.n_batch = n_batch
        self.n_threads = n_threads or os.cpu_count()
        self.use_gpu = use_gpu
        
        # Initialize the model
        self.model = None
        self._load_model()
        
        if HAYSTACK_AVAILABLE:
            super().__init__(model_name_or_path)

    def _load_model(self):
        """Load the LlamaCPP model"""
        try:
            model_path = Path(self.model_name_or_path)
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_name_or_path}")
            
            logger.info(f"Loading LlamaCPP model from: {self.model_name_or_path}")
            
            # Configure GPU usage
            n_gpu_layers = 0
            if self.use_gpu:
                try:
                    # Try to use GPU layers if available
                    n_gpu_layers = 35  # Adjust based on your GPU memory
                except Exception as e:
                    logger.warning(f"GPU not available, falling back to CPU: {e}")
            
            self.model = Llama(
                model_path=str(model_path),
                n_ctx=self.n_ctx,
                n_batch=self.n_batch,
                n_threads=self.n_threads,
                n_gpu_layers=n_gpu_layers,
                verbose=False
            )
            
            logger.info("LlamaCPP model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading LlamaCPP model: {e}")
            raise

    def invoke(self, *args, **kwargs):
        """Invoke the model - compatibility method for Haystack"""
        if args:
            prompt = args[0]
        else:
            prompt = kwargs.get('prompt', '')
        
        return self.generate(prompt, **kwargs)

    def generate(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate text using the LlamaCPP model
        
        Args:
            prompt: Input prompt
            max_tokens: Override max tokens
            temperature: Override temperature
            top_p: Override top_p
            
        Returns:
            Generated text
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Use provided parameters or defaults
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature or self.temperature
            top_p = top_p or self.top_p
            
            # Generate response
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                echo=False,  # Don't echo the prompt
                stop=["\n\n", "Human:", "Assistant:"],  # Stop sequences
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text'].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def supports(self, model_name_or_path: str, **kwargs) -> bool:
        """Check if this layer supports the given model"""
        model_path = Path(model_name_or_path)
        return model_path.exists() and model_path.suffix.lower() in ['.gguf', '.bin']

    @classmethod
    def supports_model(cls, model_name_or_path: str, **kwargs) -> bool:
        """Class method to check model support"""
        return cls(model_name_or_path, **kwargs).supports(model_name_or_path, **kwargs)

# Simplified version for when Haystack is not available
class SimpleLlamaCPP:
    """
    Simplified LlamaCPP wrapper for direct use without Haystack
    """
    
    def __init__(self, model_path: str, **kwargs):
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError("llama-cpp-python is not installed")
        
        self.model_path = model_path
        self.model = None
        self.load_model(**kwargs)
    
    def load_model(self, **kwargs):
        """Load the model"""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        self.model = Llama(
            model_path=self.model_path,
            n_ctx=kwargs.get('n_ctx', 2048),
            n_batch=kwargs.get('n_batch', 512),
            n_threads=kwargs.get('n_threads', os.cpu_count()),
            n_gpu_layers=kwargs.get('n_gpu_layers', 0),
            verbose=False
        )
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        response = self.model(
            prompt,
            max_tokens=kwargs.get('max_tokens', 512),
            temperature=kwargs.get('temperature', 0.1),
            top_p=kwargs.get('top_p', 0.95),
            echo=False
        )
        
        return response['choices'][0]['text'].strip()

# Factory function to create the appropriate model instance
def create_llama_model(model_path: str, use_haystack: bool = True, **kwargs):
    """
    Factory function to create a LlamaCPP model instance
    
    Args:
        model_path: Path to the model file
        use_haystack: Whether to use Haystack integration
        **kwargs: Additional parameters
        
    Returns:
        Model instance
    """
    if use_haystack and HAYSTACK_AVAILABLE:
        return LlamaCPPInvocationLayer(model_path, **kwargs)
    else:
        return SimpleLlamaCPP(model_path, **kwargs)
