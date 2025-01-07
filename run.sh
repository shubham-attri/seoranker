#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
YELLOW='\033[1;33m'

echo -e "${GREEN}Starting SEO Content Generator...${NC}"

# Function to check and install poetry
install_poetry() {
    echo -e "${YELLOW}Installing Poetry...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH
    export PATH="/Users/$USER/.local/bin:$PATH"
    source $HOME/.poetry/env
}

# Function to verify environment variables
verify_env() {
    local missing_vars=()
    
    # Check required environment variables
    [[ -z "${ANTHROPIC_API_KEY}" ]] && missing_vars+=("ANTHROPIC_API_KEY")
    [[ -z "${EXA_API_KEY}" ]] && missing_vars+=("EXA_API_KEY")
    [[ -z "${LANGCHAIN_API_KEY}" ]] && missing_vars+=("LANGCHAIN_API_KEY")
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo -e "${RED}Missing required environment variables:${NC}"
        printf '%s\n' "${missing_vars[@]}"
        return 1
    fi
    
    echo -e "${GREEN}All required environment variables are set${NC}"
    return 0
}

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry not found. Installing...${NC}"
    install_poetry
fi

# Initialize project if needed
if [ ! -f "pyproject.toml" ]; then
    echo -e "${YELLOW}Initializing project...${NC}"
    poetry init --name "seoranker" --description "SEO Content Generator" --author "Your Name <your.email@example.com>" --python "^3.9" --dependency "python-dotenv" --dependency "langchain" --dependency "langchain-anthropic" --dependency "langchain-exa" --dependency "exa-py" --no-interaction
fi

echo -e "${GREEN}Setting up Python environment...${NC}"
poetry env use python3
echo -e "Using virtualenv: $(poetry env info --path)"

echo -e "${GREEN}Installing/Updating dependencies...${NC}"
poetry install

# Verify environment variables
verify_env || exit 1

echo -e "${GREEN}Verifying project structure...${NC}"

# Create config if it doesn't exist
if [ ! -f "seoranker/config/settings.py" ]; then
    echo -e "${YELLOW}Creating config...${NC}"
    mkdir -p seoranker/config
    cat > seoranker/config/settings.py << EOL
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys with validation
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate required API keys
if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY not found in environment variables")
if not EXA_API_KEY:
    raise ValueError("EXA_API_KEY not found in environment variables")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

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
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
EOL
    touch seoranker/config/__init__.py
fi

# Function to configure models
configure_models() {
    echo "Model Configuration"
    echo "------------------"
    echo "1. Configure Blog Generation Model"
    echo "2. Configure Social Media Model"
    echo "3. Back to Main Menu"
    
    read -p "Select option (1-3): " choice
    
    case $choice in
        1)
            configure_model "blog"
            ;;
        2)
            configure_model "social"
            ;;
        3)
            return
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
}

configure_model() {
    task=$1
    echo "Select provider for $task generation:"
    echo "1. Anthropic (Claude)"
    echo "2. Groq (Mixtral)"
    echo "3. Local LLM"
    
    read -p "Select provider (1-3): " provider
    
    case $provider in
        1)
            model="claude-3-sonnet-20240229"
            provider_name="anthropic"
            ;;
        2)
            model="mixtral-8x7b-32768"
            provider_name="groq"
            ;;
        3)
            echo "Available local models:"
            curl -s localhost:1234/v1/models | jq -r '.data[].id'
            read -p "Enter model name: " model
            provider_name="local"
            ;;
        *)
            echo "Invalid choice"
            return
            ;;
    esac
    
    # Update config
    python -c "
from seoranker.config.model_config import ModelConfig, TaskType, ModelProvider
config = ModelConfig()
config.update_model_config(
    TaskType('$task'),
    ModelProvider('$provider_name'),
    '$model'
)
"
    echo "Configuration updated!"
}

# Main menu
while true; do
    echo -e "\nSEO Content Generator"
    echo "-------------------"
    echo "1. Run Content Generator"
    echo "2. Configure Models"
    echo "3. Exit"
    
    read -p "Select option (1-3): " choice
    
    case $choice in
        1)
            python -m seoranker.main
            ;;
        2)
            configure_models
            ;;
        3)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
done