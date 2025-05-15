import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import markdown
import http.client
import json
import os
from bs4 import BeautifulSoup

from langgraph.prebuilt import tool
from typing import Optional, Dict, List
import aiohttp
import os



@tool
async def extract_markdown_from_url(url: str) -> Dict:
    """
    Extracts structured content (headings, paragraphs) from a URL using Crawl4AI.
    
    Args:
        url (str): Valid URL to extract content from
        
    Returns:
        Dict: {
            "content": {
                "h1s": List[str],
                "h2s": List[str],
                "h3s": List[str],
                "h4s": List[str],
                "paragraphs": List[str]
            } | None,
            "error": str | None
        }
    """
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return {"content": None, "error": "Invalid URL format"}
        
        # Crawl4AI
        config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator()
        )
        
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url, config=config)
            result.markdown = result.markdown
            
            if result.success:
                with open(result.markdown.split('\n')[0].split('#')[1].strip() + ".json", "w", encoding="utf-8") as f:
                    f.write(json.dumps(extract_content_parts(result.markdown)))
                return {
                    "content": extract_content_parts(result.markdown),
                    "error": None
                }
            return {"content": None, "error": result.error_message}
            
    except Exception as e:
        return {"content": None, "error": f"Extraction failed: {str(e)}"}
    

@tool
async def search_google(query: str, gl: str = "in") -> Dict:
    """
    Performs Google search using Serper API with advanced error handling.
    
    Args:
        query (str): Search query
        gl (str): Country code (default: "in")
        
    Returns:
        Dict: {
            "organic_results": List[Dict],
            "people_also_ask": List[str],
            "related_searches": List[str],
            "error": str | None
        }
    """
    try:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return {"error": "Missing SERPER_API_KEY environment variable"}
            
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
                
                return {
                    "organic_results": data.get("organic", []),
                    "people_also_ask": data.get("peopleAlsoAsk", []),
                    "related_searches": data.get("relatedSearches", []),
                    "error": None
                }
                
    except Exception as e:
        return {
            "organic_results": [],
            "people_also_ask": [],
            "related_searches": [],
            "error": f"Search failed: {str(e)}"
        }

# def extract_markdown_from_url_imp(url: str, output_file: str = "article.json") -> str:
#     config = CrawlerRunConfig(
#         markdown_generator=DefaultMarkdownGenerator()
#     )
#     async def main():
#         async with AsyncWebCrawler() as crawler:
#             result = await crawler.arun(url, config=config)

#             if result.success:
#                 markdown = result.markdown                
#                 with open(output_file, "w", encoding="utf-8") as f:
#                     f.write(json.dumps(extract_content_parts(markdown)))
#                 print(f"Markdown saved to {output_file}")
#                 return extract_content_parts(markdown)
#             else:
#                 print("Crawl failed:", result.error_message)
#                 return ""
#     return asyncio.run(main())


# def search_google(query: str) -> dict:
#     conn = http.client.HTTPSConnection("google.serper.dev")
#     payload = json.dumps({
#         "q": query,
#         "gl": "in",
#         "relatedSearches": True,
#         "peopleAlsoAsk": True,
#         "organic": {
#             "links": True,
#             "titles": True,
#             "snippet": True
#         }
#     })
#     headers = {
#         'X-API-KEY': os.getenv("SERPER_API_KEY"),
#         'Content-Type': 'application/json'
#     }
#     conn.request("POST", "/search", payload, headers)
#     res = conn.getresponse()
#     data = res.read()
#     return json.loads(data.decode("utf-8"))

def extract_content_parts(markdown_text: str) -> dict:
    """
    Extract parts of content like headings (H1, H2, H3, H4), paragraphs, lists, and other relevant content types.
    """
    content_parts = {}
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