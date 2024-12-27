from abc import ABC, abstractmethod
from langchain_anthropic import ChatAnthropic
from seoranker.config.settings import (
    ANTHROPIC_API_KEY,
    DEFAULT_MODEL,
    TEMPERATURE,
    MAX_TOKENS
)
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            anthropic_api_key=ANTHROPIC_API_KEY,
            model=DEFAULT_MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        self.logger = logger
    
    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Main execution method to be implemented by each agent"""
        pass 