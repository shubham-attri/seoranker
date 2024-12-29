from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
from seoranker.agents.base_agent import BaseAgent
from seoranker.tools.exa_search import ExaSearchTool
from seoranker.utils.logger import setup_logger
from datetime import datetime
import re
from seoranker.config.brand_config import BrandConfig
import asyncio

logger = setup_logger(__name__)

CONTENT_TEMPLATE = """
Create comprehensive content about {keyword} optimized for SEO and social media, aligned with our brand voice.

Brand Context:
{brand_context}

Content Structure:
1. SEO Blog Post:
   - Engaging title with keyword (aligned with brand voice)
   - Meta description (155 characters)
   - Introduction with hook
   - H2 and H3 headings
   - Key points and insights
   - Expert tips
   - Latest trends
   - Interesting facts
   - Conclusion with call-to-action (using brand CTAs)
   - Recommended length: 1500-2000 words
   - Include brand perspective where relevant
   - Reference brand products/services naturally

2. Social Media Versions:
   - LinkedIn post (1300 characters)
   - Twitter thread (5-7 tweets)
   - Key hashtags (including brand hashtags)

SEO Guidelines:
- Include keyword and brand terms naturally
- Use related keywords and brand voice
- Write scannable paragraphs (2-3 sentences)
- Include bullet points and lists
- Add internal linking suggestions
- Optimize for featured snippets
- Reference brand resources where relevant

Reference Content:
{articles}

Please generate both the SEO blog post and social media versions, maintaining consistent brand voice throughout.
"""

class ContentResearchAgent(BaseAgent):
    """Agent for researching and generating content"""
    
    def __init__(self, brand_config: Optional[BrandConfig] = None):
        super().__init__()
        self.search_tool = ExaSearchTool()
        self.brand_config = brand_config
        self.prompt = PromptTemplate(
            input_variables=["keyword", "articles", "brand_context"],
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
            blog_started = False
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                    
                # Check for section markers
                if "SEO Blog Post:" in section or "Title:" in section:
                    current_section = "blog_post"
                    blog_started = True
                    parsed[current_section] = section + "\n\n"  # Include the title line
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
                
                # Add content to current section if we have one
                if current_section:
                    parsed[current_section] += section + "\n\n"
            
            # Clean up any empty sections
            parsed = {k: v.strip() for k, v in parsed.items()}
            
            # Ensure blog post starts with a title
            if parsed["blog_post"] and not any(marker in parsed["blog_post"].split('\n')[0] 
                                             for marker in ["SEO Blog Post:", "Title:", "# "]):
                parsed["blog_post"] = f"# {parsed['blog_post']}"
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing content: {str(e)}")
            return {
                "blog_post": str(content),  # Fallback to full content
                "linkedin_post": "",
                "twitter_thread": "",
                "hashtags": ""
            }
    
    def _format_brand_context(self) -> str:
        """Format brand configuration into prompt context"""
        if not self.brand_config:
            return "No specific brand guidelines provided."
        
        try:
            style_items = [
                f"- {k.replace('_', ' ').title()}: {v}"
                for k, v in self.brand_config.style_guide.items()
                if v and not isinstance(v, (list, dict))  # Only include simple string values
            ]
            style_guide = "\n".join(style_items)
            
            return f"""
Brand Name: {self.brand_config.name}
Brand Description: {self.brand_config.description}
Tone of Voice: {self.brand_config.tone_of_voice}
Target Audience: {self.brand_config.target_audience}

Key Brand Values:
{chr(10).join(f'- {value}' for value in self.brand_config.key_values)}

Style Guidelines:
{style_guide}

Products/Services to Reference:
{chr(10).join(f'- {product["name"]}: {product["description"]}' for product in self.brand_config.products)}

Preferred CTAs:
{chr(10).join(f'- {cta}' for cta in self.brand_config.cta_templates)}
"""
        except Exception as e:
            logger.warning(f"Error formatting brand context: {str(e)}")
            return f"""
Brand Name: {self.brand_config.name}
Brand Description: {self.brand_config.description}
Tone of Voice: {self.brand_config.tone_of_voice}
"""
    
    async def execute(self, keyword: str, variation_context: str = "") -> Dict[str, Any]:
        """Execute content generation"""
        try:
            # Add small delay between requests to avoid rate limits
            await asyncio.sleep(2)
            
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
            
            brand_context = self._format_brand_context()
            
            # Add variation context to prompt
            prompt_with_variation = self.prompt.template
            if variation_context:
                prompt_with_variation += f"\nVariation Focus: {variation_context}"
            
            # Generate article using LLM with variation context
            generated_content = await self.llm.ainvoke(
                PromptTemplate(
                    input_variables=["keyword", "articles", "brand_context"],
                    template=prompt_with_variation
                ).format(
                    keyword=keyword,
                    articles=articles_text,
                    brand_context=brand_context
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
                    "sources": [piece['metadata']['url'] for piece in content_pieces],
                    "brand_name": self.brand_config.name if self.brand_config else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            return {"error": str(e)} 