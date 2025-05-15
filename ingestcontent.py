"""
This file contains functions and classes related to content ingestion and analysis.
"""

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import markdown
import json
import os
from bs4 import BeautifulSoup
from pydantic import BaseModel
from db import connect_db
from typing import Optional, Dict, List
import aiohttp
import logging

if os.getenv("LOG_LEVEL") == "DEBUG":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


class ExtractContentParts(BaseModel):
    """
    Extracted content parts from a URL.
    """
    h1s: List[str]
    h2s: List[str]
    h3s: List[str]
    h4s: List[str]
    paragraphs: List[str]
    lists: List[str]
    error: Optional[str]

class SearchResults(BaseModel):
    """
    Google search results.
    """
    organic_results: List[Dict]
    people_also_ask: List[str]
    related_searches: List[str]
    error: Optional[str]

async def extract_markdown_from_url(url: str) -> ExtractContentParts:
    """
    Extracts structured content (headings, paragraphs) from a URL using Crawl4AI.
    
    Args:
        url (str): Valid URL to extract content from
        
    Returns:
        ExtractContentParts: {
            "h1s": List[str],
            "h2s": List[str],
            "h3s": List[str],
            "h4s": List[str],
                "paragraphs": List[str]
            } | None,
            "error": str | None
        }
    """
    import re
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return ExtractContentParts(h1s=[], h2s=[], h3s=[], h4s=[], paragraphs=[], lists=[], error="Invalid URL format")
        
        # Crawl4AI
        config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator()
        )
        
        async with AsyncWebCrawler() as crawler:
            logging.info(f"Crawling {url}")
            result = await crawler.arun(url, config=config)
            
            if result.success:
                logging.info(f"Successfully crawled {url}")

                os.makedirs("rawingestionfolder", exist_ok=True)
                os.makedirs("filteredcontent", exist_ok=True)
                
                title = result.markdown.split('\n')[0].split('#')[1].strip()
                safe_title = re.sub(r'[^\w\-_. ]', '_', title)
                
                with open(os.path.join("rawingestionfolder", safe_title + ".md"), "w", encoding="utf-8") as f:
                    f.write(result.markdown)
                logging.info(f"Successfully saved {url} to rrawingestionfolder")


                logging.info(f"Extracting content parts from our makedown content")
                extracted_content_parts = extract_content_parts(result.markdown)

                with open(os.path.join("filteredcontent", extracted_content_parts["h1s"][0] + ".json"), "w", encoding="utf-8") as f:
                    f.write(json.dumps(extracted_content_parts))
                logging.info(f"Successfully saved {url} to filteredcontent with title {extracted_content_parts['h1s'][0]}.json")
                
                os.rename(
                    os.path.join("rawingestionfolder", safe_title + ".md"), 
                    os.path.join("rawingestionfolder", extracted_content_parts["h1s"][0] + ".md")
                )
                logging.info(f"Successfully renamed {url} from {safe_title}.md to {extracted_content_parts['h1s'][0]}.md in rrawingestionfolder")
                
                return ExtractContentParts(
                    h1s=[], 
                    h2s=[], 
                    h3s=[], 
                    h4s=[], 
                    paragraphs=[], 
                    lists=[], 
                    error=None
                )

        
            else:
                logging.error(f"Failed to crawl {url}: {result.error_message}")
                return {
                    "h1s": [], 
                    "h2s": [], 
                    "h3s": [], 
                    "h4s": [], 
                    "paragraphs": [], 
                    "lists": [], 
                    "error": result.error_message
                }
            
            
    except Exception as e:
        logging.error(f"Failed to crawl {url}: {str(e)}")
        return {
            "h1s": [], 
            "h2s": [], 
            "h3s": [], 
            "h4s": [], 
            "paragraphs": [], 
            "lists": [], 
            "error": f"Extraction failed: {str(e)}"
        }
    

async def search_google(query: str, gl: str = "in") -> SearchResults:
    """
    Performs Google search using Serper API with advanced error handling.
    
    Args:
        query (str): Search query
        gl (str): Country code (default: "in")
        
    Returns:
        SearchResults: {
            "organic_results": List[Dict],
            "people_also_ask": List[str],
            "related_searches": List[str],
            "error": str | None
        }
    """
    try:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return SearchResults(error="Missing SERPER_API_KEY environment variable")
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": query,
                    "gl": gl,
                    "relatedSearches": True,
                    "peopleAlsoAsk": True,
                    "organic": {
                        "links": True,
                        "titles": True,
                        "snippet": True
                    }
                }
            ) as response:
                data = await response.json()



                if data.get("relatedSearches"):
                    for keyword in data["relatedSearches"]:
                        c, conn = connect_db()
                        c.execute("INSERT OR IGNORE INTO crawled (keyword, crawled) VALUES (?, ?)", (keyword["query"], 1))
                        conn.commit()
                
                if data.get("peopleAlsoAsk"):
                    for keyword in data["peopleAlsoAsk"]:
                        c, conn = connect_db()
                        c.execute("INSERT OR IGNORE INTO crawled (keyword, crawled) VALUES (?, ?)", (keyword["question"], 1))
                        conn.commit()
                
                if data.get("peopleAlsoAsk"):
                    data["peopleAlsoAsk"] = [item["question"] for item in data["peopleAlsoAsk"]]
                if data.get("relatedSearches"):
                    data["relatedSearches"] = [item["query"] for item in data["relatedSearches"]]
                
                return SearchResults(
                    organic_results=data.get("organic", []),
                    people_also_ask=data.get("peopleAlsoAsk", []),
                    related_searches=data.get("relatedSearches", []),
                    error=None
                )
                
    except Exception as e:
        return SearchResults(
            organic_results=[],
            people_also_ask=[],
            related_searches=[],
            error=f"Search failed: {str(e)}"
        )

def extract_content_parts(markdown_text: str) -> Dict:
    """
    Extract parts of content like headings (H1, H2, H3, H4), paragraphs, lists, and other relevant content types.
    """
    content_parts = {
        "h1s": [],
        "h2s": [],
        "h3s": [],
        "h4s": [],
        "paragraphs": [],
        "lists": [],
        "error": None
    }
    md = markdown.Markdown()
    html = md.convert(markdown_text)
    soup = BeautifulSoup(html, "html.parser")

    content_parts["h1s"] = [h1.text for h1 in soup.find_all("h1")]
    content_parts["h2s"] = [h2.text for h2 in soup.find_all("h2")]
    content_parts["h3s"] = [h3.text for h3 in soup.find_all("h3")]
    content_parts["h4s"] = [h4.text for h4 in soup.find_all("h4")]
    content_parts["paragraphs"] = [p.text for p in soup.find_all("p")]
    content_parts["lists"] = [li.text for li in soup.find_all("li")]

    return content_parts