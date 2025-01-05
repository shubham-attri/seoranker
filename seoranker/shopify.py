import requests

# Shopify store details
SHOPIFY_STORE = "your-store-name.myshopify.com"
ACCESS_TOKEN = "your-access-token"

# GraphQL endpoint
url = f"https://{SHOPIFY_STORE}/admin/api/2024-10/graphql.json"

# GraphQL mutation
query = """
mutation CreateArticle {
  articleCreate(article: { 
    blogId: "gid://shopify/Blog/123456789", 
    title: "My Article Title", 
    body: "<h1>Article Content</h1>", 
    tags: ["tag1", "tag2"], 
    author: "John Doe", 
    publishedAt: "2024-01-01T00:00:00Z"
  }) {
    article {
      id
      title
      body
      tags
    }
    userErrors {
      field
      message
    }
  }
}
"""

# HTTP headers
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

# Make the POST request
response = requests.post(url, json={"query": query}, headers=headers)

# Parse the response
data = response.json()
if "errors" in data:
    print("Errors:", data["errors"])
else:
    article_data = data.get("data", {}).get("articleCreate", {})
    print("Article:", article_data.get("article"))
    print("User Errors:", article_data.get("userErrors"))