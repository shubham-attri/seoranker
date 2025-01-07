from groq import Groq
from seoranker.llm.base import BaseLLM
from seoranker.config.settings import GROQ_API_KEY
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class GroqLLM(BaseLLM):
    """Groq LLM implementation"""
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "mixtral-8x7b-32768"
        self._max_tokens_limit = 32768  # Mixtral limit
    
    def generate_content(self, prompt: str, max_tokens: int = None) -> str:
        # Debug prompt
        logger.debug(f"\n=== Groq Prompt ===\nLength: {len(prompt)}\nPrompt:\n{prompt}\n=================")
        
        # If max_tokens not specified or exceeds limit, use model's limit
        if not max_tokens or max_tokens > self._max_tokens_limit:
            max_tokens = self._max_tokens_limit
            
        logger.debug(f"Generating with {self.model}, max_tokens={max_tokens}")
        
        try:
            response = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model=self.model,
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content
            logger.debug(f"\n=== Groq Response ===\nLength: {len(result)}\nFirst 100 chars: {result[:100]}\n=================")
            return result
            
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model
        
    @property
    def max_tokens_limit(self) -> int:
        """Get model's maximum token limit"""
        return self._max_tokens_limit 