#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Starting SEO Content Generator..."

# Check if virtualenv exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv || { echo -e "${RED}Failed to create virtual environment${NC}"; exit 1; }
fi

echo "Setting up Python environment..."
echo "Using virtualenv: $(pwd)/.venv"

# Activate virtualenv
source .venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment${NC}"; exit 1; }

echo "Installing/Updating dependencies..."
poetry install || { echo -e "${RED}Failed to install dependencies${NC}"; exit 1; }

echo "Verifying project structure..."

# Ensure required directories exist
mkdir -p knowledge_base output logs input

# Ensure input file exists
touch input/keywords.txt

# Main menu function
show_menu() {
    echo -e "\n${GREEN}SEO Content Generator${NC}"
    echo "-------------------"
    echo "1. Run Content Generator"
    echo "2. Configure Models"
    echo "3. Update Blog Archive"
    echo "4. Publish to Shopify"
    echo "5. Add New Keywords"
    echo "6. Exit"
    echo -n "Select option (1-6): "
}

# Main loop
while true; do
    show_menu
    read choice

    case $choice in
        1)
            echo -e "\n=== Content Generator ==="
            echo "1. Generate for single keyword"
            echo "2. Generate for all keywords"
            echo -n "Select option (1-2): "
            read gen_choice

            case $gen_choice in
                1)
                    python3 -c "from seoranker.main import generate_content; generate_content()"
                    ;;
                2)
                    python3 -c "from seoranker.main import generate_content_batch; generate_content_batch()"
                    ;;
                *)
                    echo -e "${RED}Invalid option. Please select 1-2${NC}"
                    ;;
            esac
            ;;
        2)
            python3 -c "from seoranker.config.model_config import ModelConfig; ModelConfig().configure_models()"
            ;;
        3)
            python3 -c "from seoranker.main import update_archive; update_archive()"
            ;;
        4)
            python3 -c "from seoranker.main import publish_to_shopify; publish_to_shopify()"
            ;;
        5)
            echo -e "\nAdd keywords to input/keywords.txt (one per line)"
            echo "Then press Enter to process them"
            read -p "Press Enter when ready..."
            python3 -c "from seoranker.main import add_new_keywords; add_new_keywords()"
            ;;
        6)
            echo -e "\nExiting..."
            break
            ;;
        *)
            echo -e "${RED}Invalid option. Please select 1-6${NC}"
            ;;
    esac
done

deactivate