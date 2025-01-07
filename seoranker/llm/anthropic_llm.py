from anthropic import Anthropic
from seoranker.llm.base import BaseLLM
from seoranker.config.settings import ANTHROPIC_API_KEY
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class AnthropicLLM(BaseLLM):
    """Anthropic LLM implementation"""
    
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-3-sonnet-20240229"
        self._max_tokens_limit = 4096  # Claude-3-Sonnet's actual limit
    
    def generate_content(self, prompt: str, max_tokens: int = None) -> str:
        try:
            structured_prompt = f"""
You are a professional blog writer. Generate content exactly following this structure:

<metadata>
title: [Blog post title]
meta_description: [155 character meta description]
</metadata>

<content>
[Full HTML blog post content]
</content>

Requirements:
1. Respond ONLY with the above structure (no suggestions or additional sections)
2. Use proper HTML tags (<h1>, <h2>, <h3>, <p>, <ul>, <li>)
3. Include exactly one <h1> tag
4. Include 2-3 <h2> tags
5. Format all links as <a href="url" target="_blank">text</a>
6. Ensure content is at least 2100 words

Original Prompt:
{prompt}
"""
            logger.debug(f"\n=== Claude Prompt ===\nLength: {len(structured_prompt)}\nFirst 500 chars:\n{structured_prompt[:500]}\n=================")
            
            # Calculate tokens
            response_tokens = 2500  # Reserve tokens for response
            if not max_tokens or max_tokens > response_tokens:
                max_tokens = response_tokens
                
            # Make API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": structured_prompt
                }]
            )
            
            result = response.content[0].text
            logger.debug(f"\n=== Claude Response ===\nLength: {len(result)}\nFirst 500 chars:\n{result[:500]}\n=================")
            return result
            
        except Exception as e:
            logger.error(f"Error generating content with {self.model}: {str(e)}")
            raise
    
    def get_model_name(self) -> str:
        return self.model
        
    @property
    def max_tokens_limit(self) -> int:
        """Get model's maximum token limit"""
        return self._max_tokens_limit 