import requests
import json
from seoranker.tools.exa_search import ExaSearchTool

# Replace with your actual Medium integration token and user ID
MEDIUM_TOKEN = 'your_medium_integration_token'
USER_ID = 'your_user_id'

# Function to post an article on Medium
def post_to_medium(title, content, tags, publish_status='draft'):
    headers = {
        'Authorization': f'Bearer {MEDIUM_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    url = f'https://api.medium.com/v1/users/{USER_ID}/posts'

    # Article content and metadata
    data = {
        "title": title,
        "contentFormat": "markdown",  # Choose 'html', 'markdown', or 'plain'
        "content": content,
        "tags": tags,
        "publishStatus": publish_status  # Choose 'public' or 'draft'
    }

    # Sending the POST request
    response = requests.post(url=url, headers=headers, data=json.dumps(data))

    print('Status code:', response.status_code)
    print('Response:', response.json())

def main():
    print("\n=== SEO Content Knowledge Base Builder ===")
    print("\nEnter keywords (one per line, empty line to finish):")
    keywords = []
    while True:
        keyword = input().strip()
        if not keyword:
            break
        # Clean and normalize keyword
        keyword = keyword.lower().strip()
        if keyword and keyword not in keywords:  # Avoid duplicates in input
            keywords.append(keyword)
    
    if not keywords:
        print("No keywords provided. Exiting...")
        return
    
    print(f"\nProcessing {len(keywords)} unique keywords...")
    
    # Initialize tools
    exa_tool = ExaSearchTool()
    
    # Build knowledge base
    exa_tool.build_knowledge_base(keywords)
    
    print("\nKnowledge base building complete!")
    print("You can now use 'generate_article.py' to create content using this knowledge base.")

if __name__ == "__main__":
    main()
