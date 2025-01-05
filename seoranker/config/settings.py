from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys with validation
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Validate required API keys
if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY not found in environment variables")
if not EXA_API_KEY:
    raise ValueError("EXA_API_KEY not found in environment variables")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

# LangChain Configuration
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "seoranker")

# Agent Configuration
DEFAULT_MODEL = "claude-3-sonnet-20240229"
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# Search Configuration
MAX_SEARCH_RESULTS = 5
SEARCH_TIMEOUT = 30  # seconds

# Logging Configuration
LOG_LEVEL = "DEBUG"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' 

# Add to existing settings
CONTENT_DB_PATH = "knowledge_base/content_database.csv" 