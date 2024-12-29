from typing import Dict, Any, List
from langchain.prompts import PromptTemplate
from seoranker.agents.base_agent import BaseAgent
from seoranker.tools.exa_search import ExaSearchTool
from seoranker.utils.logger import setup_logger
from datetime import datetime
import re

logger = setup_logger(__name__)

CONTENT_TEMPLATE = """
Create comprehensive content about {keyword} optimized for SEO and social media.

Content Structure:
1. SEO Blog Post:
   - Engaging title with keyword
   - Meta description (155 characters)
   - Introduction with hook
   - H2 and H3 headings
   - Key points and insights
   - Expert tips
   - Latest trends
   - Interesting facts
   - Conclusion with call-to-action
   - Recommended length: 1500-2000 words

2. Social Media Versions:
   - LinkedIn post (1300 characters)
   - Twitter thread (5-7 tweets)
   - Key hashtags

SEO Guidelines:
- Include keyword in title, first paragraph, and headings
- Use related keywords naturally
- Write scannable paragraphs (2-3 sentences)
- Include bullet points and lists
- Add internal linking suggestions
- Optimize for featured snippets

Reference Content:
{articles}

Please generate both the SEO blog post and social media versions.
"""

class ContentResearchAgent(BaseAgent):
    """Agent for researching and generating content"""
    
    def __init__(self):
        super().__init__()
        self.search_tool = ExaSearchTool()
        self.prompt = PromptTemplate(
            input_variables=["keyword", "articles"],
            template=CONTENT_TEMPLATE
        )
    
    def _parse_generated_content(self, content: str) -> Dict[str, str]:
        """Parse the generated content into different formats"""
        try:
            # Get the actual content from AIMessage
            if hasattr(content, 'content'):
                content = content.content
            
            sections = content.split("\n\n")
            parsed = {
                "blog_post": "",
                "linkedin_post": "",
                "twitter_thread": "",
                "hashtags": ""
            }
            
            current_section = None
            for section in sections:
                if "SEO Blog Post:" in section:
                    current_section = "blog_post"
                    continue
                elif "LinkedIn Post" in section:
                    current_section = "linkedin_post"
                    continue
                elif "Twitter Thread" in section:
                    current_section = "twitter_thread"
                    continue
                elif "Key Hashtags:" in section:
                    current_section = "hashtags"
                    continue
                
                if current_section:
                    parsed[current_section] += section + "\n\n"
            
            # Clean up any empty sections
            parsed = {k: v.strip() for k, v in parsed.items()}
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing content: {str(e)}")
            return {
                "blog_post": str(content),  # Fallback to full content
                "linkedin_post": "",
                "twitter_thread": "",
                "hashtags": ""
            }
    
    async def execute(self, keyword: str) -> Dict[str, Any]:
        """Execute content generation"""
        try:
            # Gather content insights
            content_pieces = self.search_tool.gather_content_insights(keyword)
            
            if not content_pieces:
                return {"error": "No content insights found"}
            
            # Format articles for content generation
            articles_text = "\n\n".join([
                f"Content {i+1} ({piece['type']}):\n"
                f"Title: {piece['title']}\n"
                f"Content: {piece['content'][:500]}..."
                for i, piece in enumerate(content_pieces)
            ])
            
            # Generate article using LLM
            generated_content = await self.llm.ainvoke(
                self.prompt.format(
                    keyword=keyword,
                    articles=articles_text
                )
            )
            
            # Parse the generated content
            parsed_content = self._parse_generated_content(generated_content)
            
            return {
                "keyword": keyword,
                **parsed_content,
                "sources_used": len(content_pieces),
                "metadata": {
                    "content_types": [piece['type'] for piece in content_pieces],
                    "generated_at": datetime.now().isoformat(),
                    "sources": [piece['metadata']['url'] for piece in content_pieces]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            return {"error": str(e)} 