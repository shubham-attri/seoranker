from typing import List, Dict, Any
from langchain_exa import ExaSearchResults
from seoranker.config.settings import EXA_API_KEY, MAX_SEARCH_RESULTS
from seoranker.utils.logger import setup_logger
from seoranker.utils.content_handler import ContentHandler

logger = setup_logger(__name__)

class ExaSearchTool:
    """Tool for gathering content insights using Exa AI"""
    
    def __init__(self):
        self.search_tool = ExaSearchResults(
            api_key=EXA_API_KEY,
            max_results=MAX_SEARCH_RESULTS
        )
        self.content_handler = ContentHandler()
    
    def gather_content_insights(self, keyword: str) -> List[Dict[str, Any]]:
        """Gather content insights for a given topic"""
        try:
            logger.info(f"Gathering content insights for: {keyword}")
            
            # Construct search queries for comprehensive coverage
            queries = [
                f"comprehensive guide {keyword}",
                f"latest trends {keyword}",
                f"expert tips {keyword}",
                f"interesting facts {keyword}"
            ]
            
            all_results = []
            for query in queries:
                search_args = {
                    "query": query,
                    "num_results": 3
                }
                
                try:
                    results = self.search_tool.invoke(search_args)
                    
                    # Log the raw response data
                    logger.info(f"\n{'='*50}\nQuery: {query}\n{'='*50}")
                    
                    # Process results directly from the response
                    if hasattr(results, 'results'):
                        for result in results.results:
                            # Only process if we have actual content
                            if hasattr(result, 'text') and hasattr(result, 'title'):
                                processed_result = {
                                    'title': getattr(result, 'title', ''),
                                    'content': getattr(result, 'text', ''),
                                    'type': query.split()[0],  # guide/trends/tips/facts
                                    'metadata': {
                                        'published_date': getattr(result, 'published_date', None),
                                        'author': getattr(result, 'author', ''),
                                        'url': getattr(result, 'url', ''),
                                        'score': getattr(result, 'score', 0.0)
                                    }
                                }
                                all_results.append(processed_result)
                                logger.info(f"Processed result: {processed_result['title']}")
                                logger.info(f"URL: {processed_result['metadata']['url']}")
                                logger.info(f"Content length: {len(processed_result['content'])}")
                
                except Exception as e:
                    logger.error(f"Error processing query '{query}': {str(e)}")
                    logger.debug("Exception details:", exc_info=True)
                    continue
            
            # Fix sorting to handle None values
            all_results.sort(
                key=lambda x: float(x['metadata'].get('score', 0) or 0),
                reverse=True
            )
            
            # Get most relevant results
            final_results = all_results[:MAX_SEARCH_RESULTS]
            
            logger.info(f"\nFinal Results Summary:")
            logger.info(f"Found {len(final_results)} relevant content pieces")
            
            if not final_results:
                logger.warning("No content found after processing results")
            else:
                # Log details about the found content
                for i, result in enumerate(final_results):
                    logger.info(f"\nResult {i+1}:")
                    logger.info(f"  Title: {result['title']}")
                    logger.info(f"  Type: {result['type']}")
                    logger.info(f"  Content length: {len(result['content'])}")
                    logger.info(f"  URL: {result['metadata']['url']}")
            
            # After processing all results, save to knowledge base
            if final_results:
                kb_result = self.content_handler.save_search_results(keyword, final_results)
                if "error" not in kb_result:
                    logger.info(f"Saved {len(final_results)} results to knowledge base")
                    return final_results
            
            return []
            
        except Exception as e:
            logger.error(f"Error in content gathering: {str(e)}")
            logger.debug("Exception details:", exc_info=True)
            return [] 