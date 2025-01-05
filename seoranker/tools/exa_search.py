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
        self._init_content_db()
    
    def _init_content_db(self):
        """Initialize content database CSV if it doesn't exist"""
        if not self.content_db_path.parent.exists():
            self.content_db_path.parent.mkdir(parents=True)
            
        if not self.content_db_path.exists():
            with open(self.content_db_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['url', 'title', 'content'])
                logger.debug(f"Created new content database at {self.content_db_path}")
    
    def _url_exists(self, url: str) -> bool:
        """Check if URL already exists in database"""
        with open(self.content_db_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return any(row['url'] == url for row in reader)
    
    def _save_content(self, url: str, title: str, content: str):
        """Save content to CSV database"""
        if not self._url_exists(url):
            with open(self.content_db_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([url, title, content])
                logger.debug(f"Saved new content from {url}")
        else:
            logger.debug(f"URL already exists in database: {url}")

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
            
            # Process organic results
            if "organic" in data:
                logger.debug(f"\nProcessing {len(data['organic'])} organic results")
                
                # E-commerce and product domains to skip
                skip_domains = [
                    "amazon", "flipkart", "myntra", "ajio", "meesho",
                    "cart", "checkout", "shop", "store"
                ]
                
                for i, result in enumerate(data["organic"], 1):
                    url = result.get("link", "")
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    
                    logger.debug(f"\nAnalyzing Result #{i}:")
                    logger.debug(f"URL: {url}")
                    logger.debug(f"Title: {title}")
                    logger.debug(f"Snippet: {snippet}")
                    
                    # Skip obvious e-commerce/product pages
                    if any(domain in url.lower() for domain in skip_domains):
                        logger.debug(f"Skipping: E-commerce/product domain")
                        continue
                    
                    # Look for informational content indicators
                    content_indicators = [
                        "guide", "how", "what", "why", "tips", "best",
                        "vs", "comparison", "difference", "review",
                        "learn", "understand", "explained", "complete",
                        "ultimate", "comprehensive"
                    ]
                    
                    # Check title and snippet for content indicators
                    text_to_check = f"{title} {snippet}".lower()
                    matches = [ind for ind in content_indicators if ind in text_to_check]
                    
                    if matches:
                        logger.debug(f"✓ Accepted: Found indicators: {matches}")
                        content_urls.append({
                            "url": url,
                            "title": title,
                            "snippet": snippet,
                            "content_type": "article"
                        })
                    else:
                        logger.debug("✗ Rejected: No content indicators")
            
            # Process "People Also Ask" content
            if "peopleAlsoAsk" in data:
                logger.debug(f"\nProcessing People Also Ask section")
                for qa in data["peopleAlsoAsk"]:
                    if not any(domain in qa["link"].lower() for domain in skip_domains):
                        content_urls.append({
                            "url": qa["link"],
                            "title": qa["question"],
                            "snippet": qa["snippet"],
                            "content_type": "qa"
                        })
                        logger.debug(f"✓ Added Q&A: {qa['question']}")
            
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
    
    def _scrape_url_content(self, url: str) -> Dict[str, Any]:
        """Scrape content from URL using Exa"""
        try:
            logger.debug(f"\n{'='*50}\nExa Content Scraping\n{'='*50}")
            logger.debug(f"Scraping URL: {url}")
            
            result = self.exa.get_contents([url], text=True)
            
            if result and result.get('results'):
                content = result['results'][0]
                
                # Save to database
                self._save_content(
                    url=content['url'],
                    title=content['title'],
                    content=content['text']
                )
                
                return {
                    'title': content['title'],
                    'content': content['text'],
                    'type': 'article',
                    'metadata': {
                        'url': content['url'],
                        'published_date': content.get('publishedDate'),
                        'author': content.get('author', '')
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
                
                content = self._scrape_url_content(url_data['url'])
                
                if content:
                    # Add snippet from SERP
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