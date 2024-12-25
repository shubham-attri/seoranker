from seo_content_generator.tools.exa_tools import ExaSearchTool
from seo_content_generator.utils.logger import setup_logger

logger = setup_logger(__name__)

def test_exa_search():
    search_tool = ExaSearchTool()
    results = search_tool.search_competitors("python web development best practices")
    
    logger.info(f"Found {len(results)} results")
    for result in results:
        logger.info(f"Title: {result['title']}")
        logger.info(f"URL: {result['url']}")
        logger.info("---")

if __name__ == "__main__":
    test_exa_search() 