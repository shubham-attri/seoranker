import csv
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import Optional, Dict, List
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class ArchiveManager:
    """Manage blog archive database"""
    
    def __init__(self):
        self.archive_path = Path("knowledge_base/blog_archive.csv")
        self.output_dir = Path("output")
        self.headers = [
            "keyword",          # Main keyword from filename
            "title",           # Article title
            "meta_description", # SEO meta description
            "file_path",       # Path to HTML file
            "status",          # draft/published/failed
            "word_count",      # Article word count
            "body"             # Full HTML content
        ]
    
    def extract_metadata_from_html(self, html_path: Path) -> Optional[Dict]:
        """Extract metadata from HTML file"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
            
            # Get keyword from filename
            keyword = html_path.stem.replace('_', ' ')
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_desc['content'].strip() if meta_desc and meta_desc.get('content') else ""
            
            # Extract title
            title = soup.find('title')
            title_text = title.text.strip() if title else ""
            
            # Extract body content - properly formatted
            body = soup.find('body')
            if body:
                # Remove any script or style tags
                for tag in body.find_all(['script', 'style']):
                    tag.decompose()
                
                # Get the formatted HTML content
                body_content = ''
                for tag in body.children:
                    if tag.name:  # Only process HTML tags, skip text nodes
                        body_content += str(tag)
            else:
                body_content = ""
            
            # Calculate word count
            word_count = len(' '.join(p.text for p in soup.find_all('p')).split())
            
            return {
                "keyword": keyword,
                "title": title_text,
                "meta_description": meta_description,
                "file_path": str(html_path.absolute()),
                "status": "draft",
                "word_count": word_count,
                "body": body_content.strip()
            }
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {html_path}: {str(e)}")
            return None
    
    def update_archive(self) -> Optional[Dict]:
        """Update blog archive from output directory"""
        try:
            existing_keywords = set()
            existing_entries = []
            
            # Read existing entries if archive exists
            if self.archive_path.exists():
                with open(self.archive_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_entries = list(reader)
                    existing_keywords = {entry["keyword"] for entry in existing_entries}
                    logger.info(f"Found {len(existing_entries)} existing entries")
            
            # Process new HTML files
            html_files = list(self.output_dir.glob("*.html"))
            new_entries = []
            skipped = []
            
            for html_file in html_files:
                keyword = html_file.stem.replace('_', ' ')
                
                if keyword in existing_keywords:
                    skipped.append(keyword)
                    logger.debug(f"Skipping existing keyword: {keyword}")
                    continue
                    
                metadata = self.extract_metadata_from_html(html_file)
                if metadata:
                    new_entries.append(metadata)
                    existing_keywords.add(keyword)
            
            # Combine existing and new entries
            all_entries = existing_entries + new_entries
            
            # Write updated archive
            with open(self.archive_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(all_entries)
            
            # Log summary
            logger.info("\nArchive Update Summary:")
            logger.info(f"Existing entries: {len(existing_entries)}")
            logger.info(f"New entries added: {len(new_entries)}")
            logger.info(f"Skipped (duplicates): {len(skipped)}")
            
            if skipped:
                logger.debug("\nSkipped keywords:")
                for keyword in skipped:
                    logger.debug(f"- {keyword}")
            
            return {
                "entries": len(all_entries),
                "new": len(new_entries),
                "skipped": len(skipped)
            }
            
        except Exception as e:
            logger.error(f"Error updating archive: {str(e)}")
            return None