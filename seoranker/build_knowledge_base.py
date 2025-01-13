from seoranker.tools.exa_search import ExaSearchTool
from seoranker.utils.logger import setup_logger
from typing import List

logger = setup_logger(__name__)

def build_knowledge_base(keywords: List[str]) -> bool:
    """Build knowledge base from a list of keywords using Exa Search"""
    try:
        logger.info(f"\nProcessing {len(keywords)} keywords...")
        
        # Initialize Exa tool
        exa_tool = ExaSearchTool()
        
        # Build knowledge base
        exa_tool.build_knowledge_base(keywords)
        
        logger.info("\n✓ Knowledge base building complete!")
        logger.info(f"Data saved in: knowledge_base/content_database.csv")
        return True
        
    except Exception as e:
        logger.error(f"Error building knowledge base: {str(e)}")
        return False

def main():
    """CLI entry point"""
    print("\n=== SEO Content Knowledge Base Builder ===")
    print("\nEnter keywords (one per line, empty line to finish):")
    
    keywords = []
    while True:
        keyword = input().strip()
        if not keyword:
            break
        # Clean and normalize keyword
        keyword = keyword.lower().strip()
        if keyword and keyword not in keywords:  # Avoid duplicates
            keywords.append(keyword)
    
    if not keywords:
        print("No keywords provided. Exiting...")
        return
    
    build_knowledge_base(keywords)

if __name__ == "__main__":
    main()