from pathlib import Path
import csv
from typing import List
from seoranker.content.blog_generator import BlogGenerator
from seoranker.content.content_archive import ContentArchive
from seoranker.utils.logger import setup_logger
import logging

# Set up root logger
logging.basicConfig(level=logging.DEBUG)
logger = setup_logger(__name__)

def get_unique_keywords() -> List[str]:
    """Get list of unique keywords from content database"""
    try:
        db_path = Path("knowledge_base/content_database.csv")
        if not db_path.exists():
            logger.error("Content database not found. Please build knowledge base first.")
            return []
            
        keywords = set()
        with open(db_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                keywords.add(row['keyword'].lower().strip())
        
        return sorted(list(keywords))
        
    except Exception as e:
        logger.error(f"Error reading keywords: {str(e)}")
        return []

def generate_content():
    """Content generation workflow"""
    try:
        print("\n=== Content Generation ===")
        
        # Get available keywords
        keywords = get_unique_keywords()
        if not keywords:
            logger.error("No keywords found in database")
            print("No keywords found in database. Please build knowledge base first.")
            return
        
        # Display keywords
        print("\nAvailable keywords:")
        for i, keyword in enumerate(keywords, 1):
            print(f"{i}. {keyword}")
        
        # Get keyword selection
        while True:
            try:
                choice = input("\nEnter keyword number (or 0 to exit): ")
                if choice == "0":
                    return
                    
                choice = int(choice)
                if 1 <= choice <= len(keywords):
                    selected_keyword = keywords[choice - 1]
                    break
                print(f"Please enter a number between 1 and {len(keywords)}")
            except ValueError:
                print("Please enter a valid number")
        
        logger.debug(f"\nSelected keyword: {selected_keyword}")
        print(f"\nGenerating content for: {selected_keyword}")
        
        # Initialize generators
        blog_generator = BlogGenerator()
        
        # Generate content
        result = blog_generator.generate_blog(selected_keyword)
        
        if result["status"] == "success":
            print("\n✓ Content generated successfully!")
            print(f"Blog ID: {result.get('blog_id')}")
            print("\nVersions generated:")
            versions = result.get("versions", {})
            print(f"- Blog post: {'✓' if versions.get('blog') else '✗'}")
            print(f"- LinkedIn: {'✓' if versions.get('linkedin') else '✗'}")
            print(f"- Twitter: {'✓' if versions.get('twitter') else '✗'}")
        else:
            print(f"\n✗ Error generating content: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error in content generation: {str(e)}", exc_info=True)
        print(f"\n✗ Error: {str(e)}")

def main():
    print("\n=== SEO Content Generator ===")
    print("\nChoose operation:")
    print("1. Build Knowledge Base")
    print("2. Generate Content")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter choice (1-3): ")
            
            if choice == "1":
                # Import here to avoid circular imports
                from seoranker.build_knowledge_base import main as build_kb
                build_kb()
                break
                
            elif choice == "2":
                generate_content()
                break
                
            elif choice == "3":
                print("\nExiting...")
                break
                
            else:
                print("Please enter a number between 1 and 3")
                
        except ValueError:
            print("Please enter a valid number")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print(f"An error occurred: {str(e)}")
            break

if __name__ == "__main__":
    main() 