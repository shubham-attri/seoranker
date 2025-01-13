import csv
import logging
from pathlib import Path
from typing import Dict, Optional
import html
import base64

logger = logging.getLogger(__name__)

class ContentArchive:
    def __init__(self):
        self.archive_path = Path("knowledge_base/blog_archive.csv")
        self.archive_path.parent.mkdir(exist_ok=True)
        
    def _encode_html(self, content: str) -> str:
        """Encode HTML content to avoid CSV parsing issues"""
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
    def _decode_html(self, encoded: str) -> str:
        """Decode HTML content from base64"""
        return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')

    def add_entry(self, entry: Dict) -> bool:
        """Add new entry to archive"""
        try:
            # Prepare headers and entry
            headers = ['keyword', 'title', 'meta_description', 'file_path', 'status', 'word_count', 'body']
            
            # Encode HTML body to avoid CSV issues
            entry['body'] = self._encode_html(entry['body'])
            
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
                        # Decode HTML body
                        row['body'] = self._decode_html(row['body'])
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
                for row in reader:
                    # Decode HTML body
                    row['body'] = self._decode_html(row['body'])
                    entries.append(row)
                    
            return entries
            
        except Exception as e:
            logger.error(f"Error getting archive entries: {str(e)}")
            return [] 