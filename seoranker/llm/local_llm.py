import requests
from seoranker.llm.base import BaseLLM
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class LocalLLM(BaseLLM):
    """Local LLM implementation using OpenAI-compatible API"""
    
    def __init__(self, model: str = "llama-3.2-3b-instruct"):
        self.base_url = "http://localhost:1234/v1"
        self.model = model
        self._max_tokens_limit = 4096  # Default, adjust based on model
    
    def generate_content(self, prompt: str, max_tokens: int = None) -> str:
        try:
            url = f"{self.base_url}/chat/completions"
            
            if not max_tokens or max_tokens > self._max_tokens_limit:
                max_tokens = self._max_tokens_limit
            
            payload = {
                "model": self.model,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()["choices"][0]["message"]["content"]
            return result
            
        except Exception as e:
            logger.error(f"Local LLM Error: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model
    
    @property
    def max_tokens_limit(self) -> int:
        return self._max_tokens_limit 