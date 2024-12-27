import asyncio
from seoranker.utils.logger import setup_logger
from seoranker.agents.research_agent import ContentResearchAgent

logger = setup_logger(__name__)

async def main():
    keyword = input("Enter the keyword for SEO article: ")
    logger.info(f"Starting content research for: {keyword}")
    
    # Initialize research agent
    agent = ContentResearchAgent()
    
    # Execute research
    result = await agent.execute(keyword)
    
    if "error" in result:
        print(f"\nError: {result['error']}")
        return
    
    # Display results
    print("\n=== Content Research Results ===")
    print(f"\nAnalyzed {result['competitor_count']} competitor articles")
    print("\nAnalysis:")
    print(result['analysis'])
    print("\nSources:")
    for url in result['sources']:
        print(f"- {url}")

if __name__ == "__main__":
    asyncio.run(main()) 