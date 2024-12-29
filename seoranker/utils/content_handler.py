import os
import json
from datetime import datetime
from pathlib import Path
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class ContentHandler:
    """Handler for saving and managing generated content"""
    
    def __init__(self):
        self.base_dir = Path("generated_content")
        self.knowledge_base_dir = Path("knowledge_base")
        # Create both directories
        self.base_dir.mkdir(exist_ok=True)
        self.knowledge_base_dir.mkdir(exist_ok=True)
    
    def _extract_title(self, content: str) -> str:
        """Extract title from blog content"""
        if not content:
            return "blog-post"
        
        # Split into lines and remove empty ones
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        for line in lines:
            # Check various title formats
            if any(marker in line for marker in ["SEO Blog Post:", "Title:", "# "]):
                # Remove markers and clean up
                title = line
                title = title.replace("SEO Blog Post:", "")
                title = title.replace("Title:", "")
                title = title.replace("# ", "")
                title = title.strip().strip('"').strip()
                
                if title:  # If we found a valid title
                    return title
        
        # If no title found, use first non-empty line
        return lines[0] if lines else "blog-post"
    
    def save_content(self, keyword: str, content: dict) -> dict:
        """Save generated content in appropriate formats"""
        try:
            # Create directory for this keyword
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content_dir = self.base_dir / f"{keyword}_{timestamp}"
            content_dir.mkdir(exist_ok=True)
            
            # Extract title from blog post content
            blog_content = content.get("blog_post", "")
            blog_title = self._extract_title(blog_content)
            
            # Create safe filename from title
            safe_title = "".join(c for c in blog_title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '-').lower()[:100]  # Limit length and make URL-friendly
            
            if not safe_title:  # Fallback if no valid title found
                safe_title = "blog-post"
            
            logger.debug(f"Extracted title: '{blog_title}'")
            logger.debug(f"Safe filename: '{safe_title}'")
            
            saved_files = {}
            
            # Save blog post
            blog_path = content_dir / f"{safe_title}.md"
            with open(blog_path, "w", encoding="utf-8") as f:
                f.write(blog_content)
            saved_files['blog'] = str(blog_path)
            
            # Save LinkedIn post
            linkedin_path = content_dir / "linkedin_post.md"
            with open(linkedin_path, "w", encoding="utf-8") as f:
                f.write("# LinkedIn Post\n\n")
                f.write(content.get("linkedin_post", ""))
            saved_files['linkedin'] = str(linkedin_path)
            
            # Save Twitter thread
            twitter_path = content_dir / "twitter_thread.md"
            with open(twitter_path, "w", encoding="utf-8") as f:
                f.write("# Twitter Thread\n\n")
                f.write(content.get("twitter_thread", ""))
            saved_files['twitter'] = str(twitter_path)
            
            # Save hashtags
            hashtags_path = content_dir / "hashtags.md"
            with open(hashtags_path, "w", encoding="utf-8") as f:
                f.write("# Key Hashtags\n\n")
                f.write(content.get("hashtags", ""))
            saved_files['hashtags'] = str(hashtags_path)
            
            # Save metadata with more details
            meta_path = content_dir / "metadata.json"
            metadata = {
                "title": blog_title,
                "keyword": keyword,
                "timestamp": timestamp,
                "files": saved_files,
                "content_stats": {
                    "blog_length": len(blog_content),
                    "linkedin_length": len(content.get("linkedin_post", "")),
                    "twitter_thread_length": len(content.get("twitter_thread", "")),
                    "hashtags_count": len(content.get("hashtags", "").split("#")) - 1
                },
                **content.get("metadata", {})
            }
            
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Content saved in directory: {content_dir}")
            logger.info(f"Blog title: {blog_title}")
            logger.info(f"Generated files: {list(saved_files.keys())}")
            
            return {
                "content_dir": str(content_dir),
                "title": blog_title,
                "files": saved_files,
                "meta_path": str(meta_path)
            }
            
        except Exception as e:
            logger.error(f"Error saving content: {str(e)}")
            return {"error": str(e)} 
    
    def save_search_results(self, keyword: str, results: list) -> dict:
        """Save raw search results to knowledge base"""
        try:
            # Create directory for this keyword in knowledge base
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            kb_dir = self.knowledge_base_dir / keyword
            kb_dir.mkdir(exist_ok=True)
            
            # Save each result as a separate markdown file
            saved_files = []
            for i, result in enumerate(results, 1):
                # Create filename from title or index if title is not available
                title = result.get('title', f'result_{i}')
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
                filename = f"{timestamp}_{safe_title}.md"
                
                file_path = kb_dir / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"# {result.get('title', 'Untitled')}\n\n")
                    f.write(f"Source: {result.get('metadata', {}).get('url', 'Unknown')}\n")
                    f.write(f"Type: {result.get('type', 'Unknown')}\n")
                    f.write(f"Date: {result.get('metadata', {}).get('published_date', 'Unknown')}\n")
                    f.write("\n---\n\n")
                    f.write(result.get('content', ''))
                
                saved_files.append(str(file_path))
            
            # Save metadata about this search
            meta_path = kb_dir / f"{timestamp}_metadata.json"
            metadata = {
                "keyword": keyword,
                "timestamp": timestamp,
                "num_results": len(results),
                "sources": [r.get('metadata', {}).get('url') for r in results],
                "saved_files": saved_files
            }
            
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Saved {len(saved_files)} results to knowledge base: {kb_dir}")
            return {
                "knowledge_base_dir": str(kb_dir),
                "saved_files": saved_files,
                "metadata_file": str(meta_path)
            }
            
        except Exception as e:
            logger.error(f"Error saving to knowledge base: {str(e)}")
            return {"error": str(e)} 