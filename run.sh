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

# Check if poetry is installed and accessible
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry not found. Installing...${NC}"
    install_poetry
fi

# Verify poetry installation
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry installation failed. Please install manually:${NC}"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    echo "export PATH=\"/Users/$USER/.local/bin:$PATH\""
    exit 1
fi

# Check if project is already set up
if [ ! -f "pyproject.toml" ]; then
    echo -e "${YELLOW}Project not initialized. Running setup...${NC}"
    bash setup.sh
else
    echo -e "${GREEN}Project already initialized${NC}"
fi

# Create and activate virtual environment
echo -e "${GREEN}Setting up Python environment...${NC}"
poetry env use python3
poetry config virtualenvs.in-project true

# Install dependencies
echo -e "${GREEN}Installing/Updating dependencies...${NC}"
poetry install --no-cache

# Check for .env file and create if needed
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}No .env file found. Creating from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${RED}Please edit .env file with your API keys before continuing${NC}"
        exit 1
    else
        echo -e "${RED}No .env.example found. Cannot create .env file${NC}"
        exit 1
    fi
fi

# Source the environment variables
set -a
source .env
set +a

# Verify environment variables
if ! verify_env; then
    echo -e "${RED}Please set all required environment variables in .env file${NC}"
    exit 1
fi

# Add this after verifying environment variables
echo -e "${GREEN}Verifying project structure...${NC}"
if [ ! -f "seoranker/config/settings.py" ]; then
    echo -e "${RED}Missing settings file. Creating...${NC}"
    # Create settings file
    mkdir -p seoranker/config
    cat > seoranker/config/settings.py << 'EOL'
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

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

# Update the test import command
echo -e "${GREEN}Running SEO Content Generator...${NC}"
poetry run python scripts/generate_article.py

echo -e "${GREEN}Done!${NC}"