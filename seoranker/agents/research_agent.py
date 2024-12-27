from typing import Dict, Any, List
from langchain.prompts import PromptTemplate
from seoranker.agents.base_agent import BaseAgent
from seoranker.tools.exa_search import ExaSearchTool
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

RESEARCH_TEMPLATE = """
Analyze the following content pieces about {keyword} and provide a comprehensive content strategy:

1. Content Types Analysis:
   - Blog post potential
   - LinkedIn post angles
   - Social media opportunities

2. Key Elements to Include:
   - Main topics and themes
   - Important statistics or data
   - Engaging hooks
   - Call-to-action ideas

3. SEO Strategy:
   - Primary and secondary keywords
   - Content structure recommendations
   - Meta description suggestions

4. Engagement Tactics:
   - Storytelling angles
   - Question prompts for engagement
   - Hashtag suggestions

Reference Content:
{articles}

Provide a detailed analysis we can use for content creation across different platforms.
"""

class ContentResearchAgent(BaseAgent):
    """Agent for researching and analyzing content"""
    
    def __init__(self):
        super().__init__()
        self.search_tool = ExaSearchTool()
        self.prompt = PromptTemplate(
            input_variables=["keyword", "articles"],
            template=RESEARCH_TEMPLATE
        )
    
    async def execute(self, keyword: str) -> Dict[str, Any]:
        """Execute content research"""
        try:
            # Search for competitor content
            competitors = self.search_tool.search_competitors(keyword)
            
            if not competitors:
                return {"error": "No competitor content found"}
            
            # Format articles for analysis
            articles_text = "\n\n".join([
                f"Content {i+1} ({comp['query_type']}):\n"
                f"Title: {comp['title']}\n"
                f"Platform: {comp['metadata']['domain']}\n"
                f"Content Preview: {comp['content'][:500]}..."
                for i, comp in enumerate(competitors)
            ])
            
            # Generate analysis using LLM
            analysis = await self.llm.ainvoke(
                self.prompt.format(
                    keyword=keyword,
                    articles=articles_text
                )
            )
            
            return {
                "keyword": keyword,
                "content_pieces": len(competitors),
                "analysis": analysis,
                "sources": [
                    {
                        "url": comp['url'],
                        "type": comp['query_type'],
                        "platform": comp['metadata']['domain']
                    }
                    for comp in competitors
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in content research: {str(e)}")
            return {"error": str(e)} 