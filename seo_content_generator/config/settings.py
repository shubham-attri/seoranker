from python_dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")

# Agent Configuration
DEFAULT_MODEL = "claude-3-sonnet-20240229"
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# Logging Configuration
LOG_LEVEL = "INFO" 