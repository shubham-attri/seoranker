import asyncio
from seoranker.utils.logger import setup_logger
from seoranker.agents.research_agent import ContentResearchAgent
from seoranker.utils.content_handler import ContentHandler

logger = setup_logger(__name__)

async def main():
    keyword = input("Enter the topic for article generation: ")
    logger.info(f"Starting content generation for: {keyword}")
    
    # Initialize agents and handlers
    agent = ContentResearchAgent()
    content_handler = ContentHandler()
    
    # Execute content generation
    result = await agent.execute(keyword)
    
    if "error" in result:
        print(f"\nError: {result['error']}")
        return
    
    # Save generated content
    save_result = content_handler.save_content(
        keyword=keyword,
        content=result
    )
    
    if "error" in save_result:
        print(f"\nError saving content: {save_result['error']}")
        return
    
    # Display results
    print("\n=== Content Generated Successfully ===")
    print(f"\nTitle: {save_result['title']}")
    print(f"Keyword: {result['keyword']}")
    print(f"Sources Used: {result['sources_used']}")
    print("\nFiles Generated:")
    for content_type, file_path in save_result['files'].items():
        print(f"- {content_type.title()}: {file_path}")
    print(f"\nMetadata: {save_result['meta_path']}")
    print(f"Content Directory: {save_result['content_dir']}")

if __name__ == "__main__":
    asyncio.run(main()) 