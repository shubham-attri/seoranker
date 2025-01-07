from seoranker.tools.exa_search import ExaSearchTool
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    print("\n=== SEO Content Knowledge Base Builder ===")
    print("\nThis tool will build a research database for your keywords.")
    print("Enter each keyword on a new line (empty line to finish):")
    
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
    
    print(f"\nProcessing {len(keywords)} unique keywords...")
    
    # Initialize Exa tool
    exa_tool = ExaSearchTool()
    
    # Build knowledge base
    exa_tool.build_knowledge_base(keywords)
    
    print("\nKnowledge base building complete!")
    print(f"Data saved in: knowledge_base/content_database.csv")

if __name__ == "__main__":
    main() 