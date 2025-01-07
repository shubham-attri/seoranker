import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class ContentArchive:
    """Manage content archives in CSV format"""
    
    def __init__(self):
        self.archive_dir = Path("knowledge_base")
        self.archive_dir.mkdir(exist_ok=True)
        
        # Define CSV paths
        self.blog_archive_path = self.archive_dir / "blog_archive.csv"
        self.social_archive_path = self.archive_dir / "social_archive.csv"
        
        # Initialize CSV files if they don't exist
        self._initialize_archives()
    
    def _initialize_archives(self):
        """Create CSV files with headers if they don't exist"""
        # Blog archive headers
        blog_headers = [
            "blog_id", 
            "keyword",
            "title",
            "meta_description",
            "file_path",
            "created_at",
            "status"
        ]
        
        # Social archive headers
        social_headers = [
            "content_id",
            "blog_id",
            "platform",
            "content",
            "created_at",
            "status"
        ]
        
        # Initialize blog archive
        if not self.blog_archive_path.exists():
            with open(self.blog_archive_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(blog_headers)
        
        # Initialize social archive
        if not self.social_archive_path.exists():
            with open(self.social_archive_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(social_headers)
    
    def save_content(self, content: Dict) -> Dict:
        """Save blog content to CSV archive"""
        try:
            # Generate blog ID
            blog_id = self._generate_blog_id()
            
            # Prepare blog row
            blog_row = {
                "blog_id": blog_id,
                "keyword": content["keyword"],
                "title": content["title"],
                "meta_description": content["meta_description"],
                "file_path": content.get("files", {}).get("blog", ""),
                "created_at": datetime.now().isoformat(),
                "status": "draft"  # Always start as draft
            }
            
            # Append to blog archive
            with open(self.blog_archive_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=blog_row.keys())
                writer.writerow(blog_row)
            
            logger.debug(f"✓ Saved blog to archive: {blog_id}")
            
            # Save social content versions
            versions = {"blog": True, "linkedin": False, "twitter": False}
            
            # Save LinkedIn version if available
            if linkedin_content := content.get("files", {}).get("linkedin"):
                self._save_social_content(
                    blog_id=blog_id,
                    platform="linkedin",
                    content=linkedin_content,
                    status="draft"
                )
                versions["linkedin"] = True
            
            # Save Twitter version if available
            if twitter_content := content.get("files", {}).get("twitter"):
                self._save_social_content(
                    blog_id=blog_id,
                    platform="twitter",
                    content=twitter_content,
                    status="draft"
                )
                versions["twitter"] = True
            
            return {
                "status": "success",
                "blog_id": blog_id,
                "timestamp": blog_row["created_at"],
                "versions": versions
            }
            
        except Exception as e:
            logger.error(f"Error saving to archive: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _save_social_content(self, blog_id: str, platform: str, content: str, status: str = "draft"):
        """Save social media content to CSV archive"""
        social_row = {
            "content_id": f"{platform}_{blog_id}",
            "blog_id": blog_id,
            "platform": platform,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "status": status
        }
        
        with open(self.social_archive_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=social_row.keys())
            writer.writerow(social_row)
    
    def get_related_content(self, keyword: str, limit: int = 3) -> Dict:
        """Get related blog posts from archive"""
        related_blogs = []
        
        try:
            with open(self.blog_archive_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Simple keyword matching for now
                    if keyword.lower() in row["keyword"].lower() or keyword.lower() in row["title"].lower():
                        related_blogs.append(row)
                        if len(related_blogs) >= limit:
                            break
            
            return {"blogs": related_blogs}
            
        except Exception as e:
            logger.error(f"Error getting related content: {str(e)}")
            return {"blogs": []}
    
    def _generate_blog_id(self) -> str:
        """Generate unique blog ID"""
        try:
            with open(self.blog_archive_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                count = sum(1 for row in reader)
            return f"blog_{count + 1}"
        except Exception:
            return "blog_1" 