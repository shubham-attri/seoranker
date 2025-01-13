from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseLLM(ABC):
    """Base class for LLM implementations"""
    
    @abstractmethod
    def generate_content(self, prompt: str, max_tokens: int = None) -> str:
        """Generate content from prompt"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name"""
        pass
    
    @property
    @abstractmethod
    def max_tokens_limit(self) -> int:
        """Get model's maximum token limit"""
        pass
    
    def handle_error(self, error: Exception) -> Optional[str]:
        """Handle model-specific errors"""
        logger.error(f"Error in {self.get_model_name()}: {str(error)}")
        return None 