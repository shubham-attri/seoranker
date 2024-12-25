# Create the project directory
cd seo_content_generator

# Initialize poetry project
poetry init --name "seo-content-generator" \
    --description "SEO Content Generator using LangChain and Exa AI" \
    --author "Your Name <your.email@example.com>" \
    --python "^3.9" \
    --dependency python-dotenv@1.0.0 \
    --dependency langchain@0.1.12 \
    --dependency langchain-anthropic@0.1.4 \
    --dependency exa-py@1.0.6 \
    --dependency requests@2.31.0 \
    --dependency beautifulsoup4@4.12.3 \
    --dev-dependency pytest@^7.4.0 \
    --no-interaction

# Create virtual environment and install dependencies
poetry install

# Create project structure
mkdir -p seo_content_generator/{config,agents,tools,utils}
mkdir -p tests
mkdir -p docs/architecture 