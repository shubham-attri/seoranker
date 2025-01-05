import requests
import json

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

if __name__ == "__main__":
    article_title = "Your Article Title"
    article_content = "# Hello World!\nThis is my first article using the Medium API."
    article_tags = ["python", "api", "medium"]

    post_to_medium(article_title, article_content, article_tags)
