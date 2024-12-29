import asyncio
import json
from pathlib import Path
from seoranker.utils.logger import setup_logger
from seoranker.agents.research_agent import ContentResearchAgent
from seoranker.utils.content_handler import ContentHandler
from seoranker.config.brand_config import BrandConfig
from typing import Optional

logger = setup_logger(__name__)

def load_brand_config(config_path: str = "config/brand.json") -> Optional[BrandConfig]:
    """Load brand configuration from JSON file"""
    try:
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path, 'r') as f:
                return BrandConfig(**json.load(f))
    except Exception as e:
        logger.warning(f"Could not load brand config: {e}")
    return None

async def main():
    # Get number of keywords with validation
    while True:
        try:
            num_keywords = input("How many topics would you like to write about? ")
            num_keywords = int(num_keywords)
            if num_keywords > 0:
                break
            print("Please enter a positive number")
        except ValueError:
            print("Please enter a valid number")
    
    # Get number of variations per keyword
    while True:
        try:
            variations_per_keyword = input("How many variations per topic? (recommended: 5) ")
            variations_per_keyword = int(variations_per_keyword)
            if variations_per_keyword > 0:
                break
            print("Please enter a positive number")
        except ValueError:
            print("Please enter a valid number")
    
    # Get keywords with validation
    keywords = []
    for i in range(num_keywords):
        while True:
            keyword = input(f"\nEnter topic #{i+1} for article generation: ").strip()
            if keyword:  # Ensure non-empty keyword
                keywords.append(keyword)
                break
            print("Please enter a valid topic")
    
    logger.info(f"Starting content generation for {len(keywords)} topics with {variations_per_keyword} variations each")
    
    # Load brand configuration
    brand_config = load_brand_config()
    if brand_config:
        logger.info(f"Loaded brand configuration for: {brand_config.name}")
    
    # Initialize agents and handlers with brand config
    agent = ContentResearchAgent(brand_config=brand_config)
    content_handler = ContentHandler()
    
    # Track success and failures
    results = {
        "successful": [],
        "failed": []
    }
    
    # Generate content for each keyword and variation
    total_articles = num_keywords * variations_per_keyword
    current_article = 0
    
    for keyword in keywords:
        print(f"\n=== Generating Articles for Topic: {keyword} ===")
        
        for variation in range(variations_per_keyword):
            current_article += 1
            try:
                print(f"\n--- Generating Variation {variation + 1}/{variations_per_keyword} ---")
                print(f"Progress: Article {current_article}/{total_articles}")
                
                # Add variation context to make each version unique
                variation_prompts = [
                    "Focus on beginner's guide and fundamentals",
                    "Emphasize advanced techniques and expert tips",
                    "Concentrate on latest trends and innovations",
                    "Highlight practical applications and real-world examples",
                    "Deep dive into specific aspects and detailed analysis"
                ]
                
                variation_context = variation_prompts[variation % len(variation_prompts)]
                
                # Execute content generation with variation
                result = await agent.execute(keyword, variation_context)
                
                if "error" in result:
                    print(f"Error generating content: {result['error']}")
                    results["failed"].append({
                        "keyword": keyword,
                        "variation": variation + 1,
                        "error": result["error"]
                    })
                    continue
                
                # Save generated content with variation number
                save_result = content_handler.save_content(
                    keyword=f"{keyword}_v{variation + 1}",
                    content=result
                )
                
                if "error" in save_result:
                    print(f"Error saving content: {save_result['error']}")
                    results["failed"].append({
                        "keyword": keyword,
                        "variation": variation + 1,
                        "error": save_result["error"]
                    })
                    continue
                
                # Display results
                print("\n=== Content Generated Successfully ===")
                print(f"Title: {save_result['title']}")
                print(f"Keyword: {keyword} (Variation {variation + 1})")
                print(f"Focus: {variation_context}")
                print(f"Sources Used: {result['sources_used']}")
                print("\nFiles Generated:")
                for content_type, file_path in save_result['files'].items():
                    print(f"- {content_type.title()}: {file_path}")
                
                results["successful"].append({
                    "keyword": keyword,
                    "variation": variation + 1,
                    "title": save_result["title"],
                    "directory": save_result["content_dir"]
                })
                
            except Exception as e:
                logger.error(f"Unexpected error processing {keyword} variation {variation + 1}: {str(e)}")
                results["failed"].append({
                    "keyword": keyword,
                    "variation": variation + 1,
                    "error": str(e)
                })
    
    # Show final summary
    print("\n=== Generation Summary ===")
    print(f"Total Topics: {len(keywords)}")
    print(f"Variations per Topic: {variations_per_keyword}")
    print(f"Total Articles Attempted: {total_articles}")
    print(f"Successfully Generated: {len(results['successful'])}")
    print(f"Failed: {len(results['failed'])}")
    
    if results["successful"]:
        print("\nSuccessful Articles:")
        for success in results["successful"]:
            print(f"- {success['keyword']} (Variation {success['variation']}): {success['title']}")
    
    if results["failed"]:
        print("\nFailed Articles:")
        for fail in results["failed"]:
            print(f"- {fail['keyword']} (Variation {fail['variation']}): {fail['error']}")

if __name__ == "__main__":
    asyncio.run(main()) 