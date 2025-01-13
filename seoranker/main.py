from pathlib import Path
import csv
from typing import List
from seoranker.content.blog_generator import BlogGenerator
from seoranker.content.content_archive import ContentArchive
from seoranker.utils.logger import setup_logger
import logging
from seoranker.utils.archive_manager import ArchiveManager
import time
import re

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

def update_archive():
    """Update blog archive from output directory"""
    try:
        print("\n=== Updating Blog Archive ===")
        manager = ArchiveManager()
        result = manager.update_archive()
        
        if result:
            print(f"\n✓ Archive updated successfully!")
            print(f"Total entries: {result['entries']}")
            print(f"New entries: {result['new']}")
            if result['skipped'] > 0:
                print(f"Skipped (duplicates): {result['skipped']}")
        else:
            print("\n✗ Error updating archive")
            
    except Exception as e:
        logger.error(f"Error in archive update: {str(e)}")
        print(f"\n✗ Error: {str(e)}")

def publish_to_shopify():
    """Publish draft articles to Shopify"""
    try:
        print("\n=== Publishing to Shopify ===")
        from seoranker.shopify import ShopifyPublisher
        
        publisher = ShopifyPublisher()
        publisher.publish_draft_articles()
        
    except Exception as e:
        logger.error(f"Error in Shopify publish: {str(e)}")
        print(f"\n✗ Error: {str(e)}")

def get_existing_keywords() -> set:
    """Get all existing keywords from both keywords.txt and content_database.csv"""
    existing_keywords = set()
    try:
        # Check keywords.txt
        kb_path = Path("knowledge_base/keywords.txt")
        if kb_path.exists():
            with open(kb_path, 'r', encoding='utf-8') as f:
                existing_keywords.update(line.strip().lower() for line in f if line.strip())
        
        # Check content_database.csv
        db_path = Path("knowledge_base/content_database.csv")
        if db_path.exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_keywords.update(row['keyword'].lower().strip() for row in reader)
                
        return existing_keywords
        
    except Exception as e:
        logger.error(f"Error reading existing keywords: {str(e)}")
        return set()

def add_new_keywords():
    """Add new keywords to knowledge base"""
    try:
        kb_path = Path("knowledge_base/keywords.txt")
        input_path = Path("input/keywords.txt")
        kb_path.parent.mkdir(exist_ok=True)
        input_path.parent.mkdir(exist_ok=True)
        
        print("\n=== Add New Keywords ===")
        print("1. Enter keywords manually")
        print("2. Import from input/keywords.txt")
        choice = input("Select option (1-2): ")
        
        new_keywords = set()
        existing_keywords = get_existing_keywords()  # Get keywords from both files
        
        if choice == "1":
            # Manual input
            print("\nEnter keywords (one per line, empty line to finish):")
            while True:
                keyword = input().strip().lower()  # Normalize to lowercase
                if not keyword:
                    break
                    
                if keyword in existing_keywords:
                    print(f"✗ Keyword already exists in database: {keyword}")
                    continue
                    
                new_keywords.add(keyword)
                print(f"✓ Added: {keyword}")
                
        elif choice == "2":
            # File input
            if not input_path.exists():
                print(f"\n✗ Input file not found: {input_path}")
                print("Please create the file and add keywords (one per line)")
                return
                
            with open(input_path, 'r', encoding='utf-8') as f:
                for line in f:
                    keyword = line.strip().lower()  # Normalize to lowercase
                    if keyword and keyword not in existing_keywords:
                        new_keywords.add(keyword)
                    elif keyword:
                        logger.debug(f"Skipping existing keyword: {keyword}")
                        
            print(f"\nProcessed {len(new_keywords)} new keywords from file")
            if len(new_keywords) == 0:
                print("All keywords already exist in database")
                return
            
        else:
            print("\n✗ Invalid option")
            return
            
        if new_keywords:
            # Append new keywords to file
            with open(kb_path, 'a', encoding='utf-8') as f:
                for keyword in new_keywords:
                    f.write(f"{keyword}\n")
            
            # Clear input file after successful import
            if choice == "2":
                input_path.write_text("")
            
            print(f"\n✓ Added {len(new_keywords)} new keywords to knowledge base")
            
            # Build knowledge base using Exa Search
            print("\nBuilding knowledge base for new keywords...")
            from seoranker.build_knowledge_base import build_knowledge_base
            if build_knowledge_base(list(new_keywords)):
                print("\n✓ Knowledge base updated successfully!")
            else:
                print("\n✗ Error updating knowledge base. Check logs for details.")
            
        else:
            print("\nℹ No new keywords added")
            
    except Exception as e:
        logger.error(f"Error adding keywords: {str(e)}")
        print(f"\n✗ Error: {str(e)}")

def sanitize_filename(keyword: str) -> str:
    """Sanitize keyword for filename"""
    # Replace spaces and special characters with underscore
    sanitized = re.sub(r'[^\w\s-]', '', keyword.lower())
    return re.sub(r'[-\s]+', '_', sanitized)

def get_existing_content() -> set:
    """Get set of existing content keywords"""
    output_dir = Path("output")
    existing = set()
    
    if output_dir.exists():
        for file in output_dir.glob("*.html"):
            # Convert filename back to keyword format
            keyword = file.stem.replace('_', ' ').lower()
            existing.add(keyword)
    
    return existing

def get_valid_keywords() -> dict:
    """Get dictionary of valid keywords from content database with their normalized form"""
    try:
        db_path = Path("knowledge_base/content_database.csv")
        if not db_path.exists():
            return {}
            
        valid_keywords = {}
        with open(db_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Store original keyword as key and normalized form as value
                keyword = row['keyword'].strip()
                normalized = keyword.lower()
                valid_keywords[normalized] = keyword
                
        return valid_keywords
        
    except Exception as e:
        logger.error(f"Error reading valid keywords: {str(e)}")
        return {}

def generate_content_batch():
    """Generate content for all keywords in database that don't have existing output"""
    try:
        print("\n=== Batch Content Generation ===")
        
        # Get valid keywords from database
        valid_keywords = get_valid_keywords()
        if not valid_keywords:
            logger.error("No keywords found in database")
            print("No keywords found in database. Please build knowledge base first.")
            return
            
        # Filter out keywords that already have content
        existing_content = get_existing_content()
        pending_keywords = []
        
        # Use normalized keywords for comparison but keep original case
        for normalized, original in valid_keywords.items():
            if normalized not in existing_content:
                pending_keywords.append(original)
        
        if not pending_keywords:
            print("\nℹ All keywords already have content generated")
            return
            
        print(f"\nFound {len(pending_keywords)} keywords pending content generation:")
        for i, keyword in enumerate(pending_keywords, 1):
            print(f"{i}. {keyword}")
            
        # Confirm with user
        confirm = input("\nGenerate content for all pending keywords? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled")
            return
            
        # Initialize generators
        blog_generator = BlogGenerator()
        
        # Process each keyword
        for i, keyword in enumerate(pending_keywords, 1):
            print(f"\n[{i}/{len(pending_keywords)}] Generating content for: {keyword}")
            
            result = blog_generator.generate_blog(keyword)
            
            if result["status"] == "success":
                print(f"✓ Content generated successfully!")
                print(f"Blog ID: {result.get('blog_id')}")
                versions = result.get("versions", {})
                print(f"- Blog post: {'✓' if versions.get('blog') else '✗'}")
                print(f"- LinkedIn: {'✓' if versions.get('linkedin') else '✗'}")
                print(f"- Twitter: {'✓' if versions.get('twitter') else '✗'}")
            else:
                print(f"✗ Error: {result.get('error', 'Unknown error')}")
            
            # Add delay between keywords
            if i < len(pending_keywords):
                time.sleep(2)
                
        print("\n=== Batch Generation Complete ===")
        print(f"Processed {len(pending_keywords)} keywords")
            
    except Exception as e:
        logger.error(f"Error in batch content generation: {str(e)}", exc_info=True)
        print(f"\n✗ Error: {str(e)}")

def main():
    """Main application entry point"""
    try:
        while True:
            print("\nSEO Content Generator")
            print("-------------------")
            print("1. Run Content Generator")
            print("2. Configure Models")
            print("3. Update Blog Archive")
            print("4. Publish to Shopify")
            print("5. Add New Keywords")  # New option
            print("6. Exit")
            
            choice = input("Select option (1-6): ")
            
            if choice == "1":
                run_content_generator()
            elif choice == "2":
                configure_models()
            elif choice == "3":
                update_archive()
            elif choice == "4":
                publish_to_shopify()
            elif choice == "5":
                add_new_keywords()  # New function
            elif choice == "6":
                print("\nExiting...")
                break
            else:
                print("\n✗ Invalid option. Please try again.")
                
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 