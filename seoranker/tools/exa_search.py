from typing import List, Dict, Any
import http.client
import json
import time
import csv
import os
from pathlib import Path
from exa_py import Exa
from seoranker.config.settings import EXA_API_KEY, SERPER_API_KEY, MAX_SEARCH_RESULTS
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class ExaSearchTool:
    """Tool for gathering content insights using Serper and Exa AI"""
    
    def __init__(self):
        self.exa = Exa(api_key=EXA_API_KEY)
        self.content_db_path = Path("knowledge_base/content_database.csv")
        self.suggestions_db_path = Path("knowledge_base/suggestions_database.csv")
        self._init_databases()
    
    def _init_databases(self):
        """Initialize both databases if they don't exist"""
        # Content database
        if not self.content_db_path.parent.exists():
            self.content_db_path.parent.mkdir(parents=True)
        
        if not self.content_db_path.exists():
            with open(self.content_db_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['keyword', 'url', 'title', 'content'])
        
        # Suggestions database
        if not self.suggestions_db_path.exists():
            with open(self.suggestions_db_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['source_keyword', 'question', 'title', 'url'])
    
    def _url_exists(self, keyword: str, url: str) -> bool:
        """Check if URL already exists in database for this keyword"""
        try:
            if not self.content_db_path.exists():
                return False
            
            with open(self.content_db_path, 'r', encoding='utf-8') as f:
                # Skip empty files
                if f.readline().strip() == '':
                    return False
                
                # Go back to start of file
                f.seek(0)
                reader = csv.DictReader(f)
                
                # Handle missing columns
                if not reader.fieldnames or 'keyword' not in reader.fieldnames:
                    return False
                
                return any(row.get('keyword') == keyword and row.get('url') == url 
                          for row in reader)
                          
        except Exception as e:
            logger.error(f"Error checking URL existence: {str(e)}")
            return False
    
    def _save_content(self, keyword: str, url: str, title: str, content: str):
        """Save content to CSV database"""
        try:
            # Create file with headers if it doesn't exist
            if not self.content_db_path.exists():
                with open(self.content_db_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['keyword', 'url', 'title', 'content'])
            
            if not self._url_exists(keyword, url):
                with open(self.content_db_path, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([keyword, url, title, content])
                    logger.debug(f"Saved new content from {url} for keyword '{keyword}'")
            else:
                logger.debug(f"URL already exists in database for keyword '{keyword}': {url}")
            
        except Exception as e:
            logger.error(f"Error saving content: {str(e)}")
            logger.debug("Exception details:", exc_info=True)
    
    def _save_suggestion(self, source_keyword: str, question: str, title: str, url: str):
        """Save a suggestion to the suggestions database"""
        with open(self.suggestions_db_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([source_keyword, question, title, url])
    
    def _get_serp_results(self, keyword: str) -> List[Dict[str, Any]]:
        """Get search results from Serper API"""
        try:
            logger.debug(f"\n{'='*50}\nSerper API Search\n{'='*50}")
            logger.debug(f"Searching for keyword: {keyword}")
            
            if not SERPER_API_KEY:
                logger.error("SERPER_API_KEY not found in environment variables")
                return []
            
            logger.debug(f"Using Serper API Key: {SERPER_API_KEY[:5]}...")
            
            conn = http.client.HTTPSConnection("google.serper.dev")
            payload = json.dumps({
                "q": keyword,
                "gl": "in",  # Geolocation: India
                "num": 10    # Get more results to filter
            })
            
            headers = {
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json'
            }
            
            conn.request("POST", "/search", payload, headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            
            logger.debug("\nParsed Response:")
            logger.debug(json.dumps(data, indent=2))
            
            content_urls = []
            
            # E-commerce and product domains to skip
            skip_domains = [
                "amazon", "flipkart", "myntra", "ajio", "meesho",
                "checkout", "cart"  # Removed generic "shop" and "store"
            ]
            
            # Look for informational content indicators
            content_indicators = [
                # Question-based
                "guide", "how", "what", "why", "tips", "best",
                # Comparison
                "vs", "comparison", "difference", "review",
                # Educational
                "learn", "understand", "explained", "complete",
                "ultimate", "comprehensive",
                # Coffee-specific
                "brewing", "roasting", "taste", "flavor", "aroma",
                "benefits", "types", "varieties", "process",
                # Generic informational
                "about", "guide", "introduction", "overview",
                "features", "characteristics", "details"
            ]
            
            # Process organic results
            if "organic" in data:
                logger.debug(f"\nProcessing {len(data['organic'])} organic results")
                
                for i, result in enumerate(data["organic"], 1):
                    url = result.get("link", "")
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    
                    logger.debug(f"\nAnalyzing Result #{i}:")
                    logger.debug(f"URL: {url}")
                    logger.debug(f"Title: {title}")
                    logger.debug(f"Snippet: {snippet}")
                    
                    # Skip obvious e-commerce/checkout pages
                    if any(domain in url.lower() for domain in skip_domains):
                        logger.debug(f"Skipping: E-commerce domain")
                        continue
                    
                    # Check title and snippet for content indicators
                    text_to_check = f"{title} {snippet}".lower()
                    matches = [ind for ind in content_indicators if ind in text_to_check]
                    
                    # Accept if has content indicators or looks informative
                    if matches or "%" in text_to_check or "coffee" in text_to_check:
                        logger.debug(f"✓ Accepted: Found indicators: {matches}")
                        content_urls.append({
                            "url": url,
                            "title": title,
                            "snippet": snippet,
                            "content_type": "article"
                        })
            
            # Process "People Also Ask" content
            if "peopleAlsoAsk" in data:
                logger.debug("\nProcessing People Also Ask section")
                for qa in data["peopleAlsoAsk"]:
                    # Always save to suggestions database
                    self._save_suggestion(
                        source_keyword=keyword,
                        question=qa['question'],
                        title=qa.get('title', ''),
                        url=qa.get('link', '')
                    )
                    logger.debug(f"✓ Added Q&A: {qa['question']}")
                    
                    # Add to content URLs if not from skipped domains
                    if not any(domain in qa['link'].lower() for domain in skip_domains):
                        content_urls.append({
                            "url": qa["link"],
                            "title": qa["question"],
                            "snippet": qa["snippet"],
                            "content_type": "qa"
                        })
            
            logger.debug(f"\n{'='*50}")
            logger.debug(f"Found {len(content_urls)} content-focused URLs")
            for i, url_data in enumerate(content_urls[:MAX_SEARCH_RESULTS], 1):
                logger.debug(f"\nAccepted URL #{i}:")
                logger.debug(f"Title: {url_data['title']}")
                logger.debug(f"URL: {url_data['url']}")
                logger.debug(f"Type: {url_data['content_type']}")
            
            return content_urls[:MAX_SEARCH_RESULTS]
            
        except Exception as e:
            logger.error(f"Error in Serper API: {str(e)}")
            logger.debug("Exception details:", exc_info=True)
            return []
    
    def _scrape_url_content(self, keyword: str, url: str) -> Dict[str, Any]:
        """Scrape content from URL using Exa"""
        try:
            logger.debug(f"\n{'='*50}\nExa Content Scraping\n{'='*50}")
            logger.debug(f"Scraping URL: {url}")
            
            result = self.exa.get_contents([url], text=True)
            
            if result and hasattr(result, 'results') and result.results:
                content = result.results[0]  # First result
                
                # Save to database with keyword
                self._save_content(
                    keyword=keyword,
                    url=content.url,
                    title=content.title,
                    content=content.text
                )
                
                return {
                    'title': content.title,
                    'content': content.text,
                    'type': 'article',
                    'metadata': {
                        'url': content.url,
                        'published_date': getattr(content, 'publishedDate', None),
                        'author': getattr(content, 'author', '')
                    }
                }
            
            logger.debug("❌ Failed: No content returned from Exa")
            return None
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            logger.debug("Exception details:", exc_info=True)
            return None
    
    def gather_content_insights(self, keyword: str) -> List[Dict[str, Any]]:
        """Gather content insights for a given topic"""
        try:
            logger.info(f"\n{'='*50}\nContent Gathering Started\n{'='*50}")
            logger.info(f"Topic: {keyword}")
            
            # Get relevant URLs from Serper
            content_urls = self._get_serp_results(keyword)
            
            if not content_urls:
                logger.warning("No content URLs found")
                return []
            
            # Scrape content from each URL
            all_results = []
            for i, url_data in enumerate(content_urls, 1):
                logger.info(f"\nProcessing URL {i}/{len(content_urls)}")
                logger.info(f"URL: {url_data['url']}")
                
                content = self._scrape_url_content(keyword, url_data['url'])
                
                if content:
                    content['serp_snippet'] = url_data['snippet']
                    all_results.append(content)
                    logger.info("✓ Successfully scraped and processed")
                else:
                    logger.info("✗ Failed to scrape content")
                
                # Add delay between requests
                time.sleep(1)
            
            logger.info(f"\n{'='*50}\nGathering Complete\n{'='*50}")
            logger.info(f"Successfully gathered content from {len(all_results)}/{len(content_urls)} URLs")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error in content gathering: {str(e)}")
            logger.debug("Exception details:", exc_info=True)
            return [] 
    
    def _keyword_exists(self, keyword: str) -> bool:
        """Check if exact keyword already exists in database"""
        try:
            if not self.content_db_path.exists():
                return False
            
            # Normalize the keyword
            keyword = keyword.lower().strip()
            
            with open(self.content_db_path, 'r', encoding='utf-8') as f:
                # Skip empty files
                if f.readline().strip() == '':
                    return False
                
                # Go back to start of file
                f.seek(0)
                reader = csv.DictReader(f)
                
                # Handle missing columns
                if not reader.fieldnames or 'keyword' not in reader.fieldnames:
                    return False
                
                # Check for exact keyword match
                for row in reader:
                    existing_keyword = row.get('keyword', '').lower().strip()
                    if existing_keyword == keyword:
                        logger.info(f"Exact match found: '{keyword}' already exists in database")
                        return True
                      
                logger.debug(f"No exact match found for '{keyword}'")
                return False
                      
        except Exception as e:
            logger.error(f"Error checking keyword existence: {str(e)}")
            return False
    
    def build_knowledge_base(self, keywords: List[str]) -> None:
        """Build knowledge base from a list of keywords"""
        logger.info(f"\n{'='*50}\nKnowledge Base Building Started\n{'='*50}")
        logger.info(f"Processing {len(keywords)} keywords")
        
        for i, keyword in enumerate(keywords, 1):
            logger.info(f"\nProcessing keyword {i}/{len(keywords)}: '{keyword}'")
            
            # Check if keyword exists using dedicated method
            if self._keyword_exists(keyword):
                logger.info(f"✓ Keyword '{keyword}' already exists in database - skipping")
                continue
            
            logger.info(f"⚡ Gathering content for keyword: {keyword}")
            content_results = self.gather_content_insights(keyword)
            
            if content_results:
                logger.info(f"✓ Added {len(content_results)} articles for '{keyword}'")
            else:
                logger.warning(f"✗ No content found for '{keyword}'")
            
            # Add delay between keywords
            if i < len(keywords):
                time.sleep(2)
        
        logger.info(f"\n{'='*50}\nKnowledge Base Building Complete\n{'='*50}") 