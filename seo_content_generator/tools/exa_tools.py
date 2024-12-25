from exa_py import Client
from seo_content_generator.config.settings import EXA_API_KEY
from seo_content_generator.utils.logger import setup_logger

logger = setup_logger(__name__)

class ExaSearchTool:
    def __init__(self):
        self.client = Client(EXA_API_KEY)
        
    def search_competitors(self, keyword, num_results=5):
        """
        Search for top competitor content for a given keyword
        """
        try:
            results = self.client.search(
                keyword,
                num_results=num_results,
                use_autoprompt=True
            )
            return [
                {
                    'title': result.title,
                    'url': result.url,
                    'snippet': result.text
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error searching Exa: {str(e)}")
            return [] 