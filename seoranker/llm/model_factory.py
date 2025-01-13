from typing import Dict
from seoranker.llm.base import BaseLLM
from seoranker.llm.anthropic_llm import AnthropicLLM
from seoranker.llm.groq_llm import GroqLLM
from seoranker.llm.local_llm import LocalLLM
from seoranker.config.model_config import ModelProvider
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class ModelFactory:
    @staticmethod
    def create_llm(config: Dict) -> BaseLLM:
        provider = config["provider"]
        model = config["model"]
        
        try:
            if provider == ModelProvider.ANTHROPIC.value:
                return AnthropicLLM()
            elif provider == ModelProvider.GROQ.value:
                return GroqLLM()
            elif provider == ModelProvider.LOCAL.value:
                return LocalLLM(model=model)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            logger.warning(f"Failed to initialize {provider} LLM: {str(e)}")
            logger.info("Falling back to local LLM")
            return LocalLLM(model="llama-3.2-3b-instruct") 