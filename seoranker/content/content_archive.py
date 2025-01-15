import csv
import logging
from pathlib import Path
from typing import Dict, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ContentArchive:
    def __init__(self):
        self.archive_path = Path("knowledge_base/blog_archive.csv")
        self.archive_path.parent.mkdir(exist_ok=True)

    def _extract_body_content(self, html_content: str) -> str:
        """Extract clean body content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            body = soup.find('body')
            
            if not body:
                return html_content
            
            # Remove any script or style tags
            for tag in body.find_all(['script', 'style']):
                tag.decompose()
            
            # Get all content within body, preserving HTML structure
            return ''.join(str(tag) for tag in body.children if tag.name)
            
        except Exception as e:
            logger.error(f"Error extracting body content: {str(e)}")
            return html_content

    def add_entry(self, entry: Dict) -> bool:
        """Add new entry to archive"""
        try:
            # Prepare headers and entry
            headers = ['keyword', 'title', 'meta_description', 'file_path', 'status', 'word_count', 'body']
            
            # Extract clean body content
            entry['body'] = self._extract_body_content(entry['body'])
            
            # Create file with headers if it doesn't exist
            if not self.archive_path.exists():
                with open(self.archive_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
            
            # Append entry
            with open(self.archive_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writerow(entry)
                
            logger.info(f"Added entry for keyword: {entry['keyword']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding archive entry: {str(e)}")
            return False
            
    def get_entry(self, keyword: str) -> Optional[Dict]:
        """Get entry by keyword"""
        try:
            if not self.archive_path.exists():
                return None
                
            with open(self.archive_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['keyword'].lower() == keyword.lower():
                        return row
                        
            return None
            
        except Exception as e:
            logger.error(f"Error getting archive entry: {str(e)}")
            return None

    def get_all_entries(self) -> list:
        """Get all archive entries"""
        try:
            entries = []
            if not self.archive_path.exists():
                return entries
                
            with open(self.archive_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                entries = list(reader)
                    
            return entries
            
        except Exception as e:
            logger.error(f"Error getting archive entries: {str(e)}")
            return [] 