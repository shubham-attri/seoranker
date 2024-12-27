from typing import List, Dict, Any
from langchain_exa import ExaSearchResults
from seoranker.config.settings import EXA_API_KEY, MAX_SEARCH_RESULTS
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class ExaSearchTool:
    """Tool for searching and analyzing content using Exa AI"""
    
    def __init__(self):
        self.search_tool = ExaSearchResults(
            api_key=EXA_API_KEY,
            max_results=MAX_SEARCH_RESULTS
        )
    
    def search_competitors(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for top competitor content for a given keyword"""
        try:
            logger.info(f"Searching competitors for keyword: {keyword}")
            
            # Construct search queries for different content types
            queries = [
                f"best blog posts about {keyword}",
                f"viral LinkedIn posts about {keyword}",
                f"trending articles {keyword}",
                f"successful content {keyword} examples"
            ]
            
            all_results = []
            for query in queries:
                # Execute search using invoke as per API docs
                search_args = {
                    "query": query,
                    "num_results": 3  # Get top 3 from each category
                }
                
                results = self.search_tool.invoke(search_args)
                
                # Process results
                if isinstance(results, dict) and 'results' in results:
                    for result in results['results']:
                        processed_result = {
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'content': result.get('text', ''),
                            'score': result.get('score', 0.0),
                            'query_type': query.split()[0],  # blog/LinkedIn/article
                            'metadata': {
                                'length': len(result.get('text', '')),
                                'has_title': bool(result.get('title')),
                                'domain': result.get('url', '').split('/')[2] if result.get('url') else None
                            }
                        }
                        all_results.append(processed_result)
            
            # Sort by score and get top results
            all_results.sort(key=lambda x: x['score'], reverse=True)
            top_results = all_results[:MAX_SEARCH_RESULTS]
            
            logger.info(f"Found {len(top_results)} relevant content pieces")
            return top_results
            
        except Exception as e:
            logger.error(f"Error in competitor search: {str(e)}")
            return [] 