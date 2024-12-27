#!/bin/bash

# Initialize poetry project
poetry init --name "seoranker" \
    --description "SEO Content Generator using LangChain and Exa AI" \
    --author "Shubham Attri <your.email@example.com>" \
    --python "^3.9" \
    --dependency "python-dotenv" \
    --dependency "langchain" \
    --dependency "langchain-anthropic" \
    --dependency "langchain-exa" \
    --no-interaction

# Create project structure
mkdir -p seoranker/{agents,tools,utils,config}
mkdir -p tests
mkdir -p docs/architecture

# Create initial files
touch seoranker/__init__.py
touch seoranker/agents/__init__.py
touch seoranker/tools/__init__.py
touch seoranker/utils/__init__.py
touch seoranker/config/__init__.py

# Create .env template
cat > .env.example << EOL
ANTHROPIC_API_KEY=your-anthropic-key
EXA_API_KEY=your-exa-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=seoranker
EOL

# Create .gitignore
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
.env
.venv/
venv/

# IDE
.vscode/
.idea/

# Project specific
*.log
.DS_Store
EOL

# Initialize git
git init 