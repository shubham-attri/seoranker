import requests
from datetime import datetime
import json
from pathlib import Path
import csv
from typing import Dict, Optional, List, Any
from seoranker.utils.logger import setup_logger
import os
from bs4 import BeautifulSoup

logger = setup_logger(__name__)

class ShopifyPublisher:
    """Handle publishing articles to Shopify"""
    
    def __init__(self):
        """Initialize Shopify publisher"""
        self.store = os.getenv("SHOPIFY_STORE")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        
        if not all([self.store, self.access_token]):
            raise ValueError("Missing required Shopify environment variables")
            
        self.archive_path = Path("knowledge_base/blog_archive.csv")
        self.author = "Shubham Attri"
        
        # Get or create blog
        self.blog_id = self._get_or_create_blog()
        
    def _execute_graphql(self, query: str, variables: dict = None) -> dict:
        """Execute GraphQL query/mutation"""
        response = requests.post(
            f"https://{self.store}/admin/api/2024-10/graphql.json",
            json={"query": query, "variables": variables},
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": self.access_token
            }
        )
        return response.json()
    
    def _get_or_create_blog(self) -> str:
        """Get existing blog or create new one"""
        # Query existing blogs
        query = """
        query GetBlogs {
          blogs(first: 10) {
            edges {
              node {
                id
                title
              }
            }
          }
        }
        """
        
        response = self._execute_graphql(query)
        blogs = response.get("data", {}).get("blogs", {}).get("edges", [])
        
        if blogs:
            blog_id = blogs[0]["node"]["id"]
            logger.info(f"Using existing blog: {blogs[0]['node']['title']} ({blog_id})")
            return blog_id
            
        # Create new blog if none exist
        mutation = """
        mutation CreateBlog {
          blogCreate(blog: { 
            title: "Helpful Blogs", 
            commentPolicy: AUTO_PUBLISHED 
          }) {
            blog {
              id
              title
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        
        response = self._execute_graphql(mutation)
        blog = response.get("data", {}).get("blogCreate", {}).get("blog")
        
        if blog:
            logger.info(f"Created new blog: {blog['title']} ({blog['id']})")
            return blog["id"]
            
        raise ValueError("Failed to get or create blog")
    
    def _update_archive_status(self, entry: Dict, new_status: str):
        """Update article status in archive"""
        try:
            # Read current archive
            with open(self.archive_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                entries = list(reader)
                fieldnames = reader.fieldnames

            # Update status for matching entry
            for e in entries:
                if e["title"] == entry["title"]:
                    e["status"] = new_status
                    logger.debug(f"Updated status for '{entry['title']}' to {new_status}")
                    break

            # Write updated archive
            with open(self.archive_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(entries)

        except Exception as e:
            logger.error(f"Error updating archive status: {str(e)}")
    
    def create_article(self, entry: Dict) -> Optional[Dict]:
        """Create article in Shopify"""
        try:
            # Get clean body content
            body = entry["body"]
            
            # Remove H1 tag if present (since title is set separately)
            soup = BeautifulSoup(body, 'html.parser')
            h1_tag = soup.find('h1')
            if h1_tag:
                h1_tag.decompose()
                body = str(soup)
            
            mutation = """
            mutation CreateArticle($blogId: ID!) {
              articleCreate(article: { 
                blogId: $blogId, 
                title: "%s", 
                body: "%s", 
                summary: "%s", 
                tags: ["%s", "SEO Blog"], 
                author: { name: "%s" },
                metafields: [
                  {
                    namespace: "seo",
                    key: "description", 
                    type: "single_line_text_field",
                    value: "%s"
                  }
                ]
              }) {
                article {
                  id
                  title
                  handle
                }
                userErrors {
                  field
                  message
                }
              }
            }
            """ % (
                entry["title"].replace('"', '\\"'),
                body.replace('"', '\\"'),
                entry.get("meta_description", "").replace('"', '\\"'),
                entry["keyword"].replace('"', '\\"'),
                self.author.replace('"', '\\"'),
                entry.get("meta_description", "").replace('"', '\\"')
            )
            
            variables = {"blogId": self.blog_id}
            response = self._execute_graphql(mutation, variables)
            
            article = response.get("data", {}).get("articleCreate", {})
            if article.get("userErrors"):
                errors = article["userErrors"]
                error_msg = "; ".join(f"{e['field']}: {e['message']}" for e in errors)
                logger.error(f"Failed to create article: {error_msg}")
                return None
            
            if article.get("article"):
                article_data = article["article"]
                logger.info(f"Created article: {article_data['title']} ({article_data['id']})")
                # Update status to published
                self._update_archive_status(entry, "published")
                return article_data
            
            logger.error("Failed to create article: Unknown error")
            return None
            
        except Exception as e:
            logger.error(f"Error creating article: {str(e)}")
            # Update status to failed
            self._update_archive_status(entry, "failed")
            return None
    
    def publish_draft_articles(self):
        """Publish all draft and failed articles from archive"""
        try:
            logger.info("\n=== Starting Batch Publish ===")
            
            # Load and validate archive
            if not self.archive_path.exists():
                logger.error("Archive file not found")
                print("\n✗ Error: Blog archive not found")
                return
            
            # Process archive
            with open(self.archive_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                entries = list(reader)
                
                # Show archive status
                logger.info(f"\nArchive Status:")
                logger.info(f"Total Articles: {len(entries)}")
                
                status_counts = {}
                for entry in entries:
                    status = entry["status"]
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                for status, count in status_counts.items():
                    logger.info(f"{status}: {count}")
                
                # Get articles to publish (both draft and failed)
                to_publish = [e for e in entries if e["status"] in ["draft", "failed"]]
                total = len(to_publish)
                
                if total == 0:
                    logger.info("\n✗ No articles found to publish")
                    return
                    
                logger.info(f"\nFound {total} articles to publish")
                print(f"\nProcessing {total} articles...")
                
                published = []
                failed = []
                
                # Process each article
                for i, entry in enumerate(to_publish, 1):
                    logger.debug(f"\n--- Publishing Article {i}/{total} ---")
                    logger.debug(f"Title: {entry['title']}")
                    logger.debug(f"Status: {entry['status']}")
                    
                    print(f"\nPublishing ({i}/{total}): {entry['title']}")
                    print(f"Current Status: {entry['status']}")
                    
                    result = self.create_article(entry)
                    if result:
                        published.append({
                            'title': entry['title'],
                            'id': result['id'],
                            'handle': result.get('handle', '')
                        })
                        logger.info(f"✓ Successfully published: {result['id']}")
                        print(f"✓ Success!")
                    else:
                        failed.append(entry['title'])
                        logger.error(f"✗ Failed to publish: {entry['title']}")
                        print(f"✗ Failed")
                
                # Print summary
                print("\n=== Publishing Summary ===")
                
                if published:
                    print("\nSuccessfully published:")
                    for title in published:
                        print(f"✓ {title}")
                
                if failed:
                    print("\nFailed to publish:")
                    for title in failed:
                        print(f"✗ {title}")
                
                print(f"\nTotal: {total} | Success: {len(published)} | Failed: {len(failed)}")
                
        except Exception as e:
            logger.error(f"Error publishing articles: {str(e)}")
            print(f"\n✗ Error: {str(e)}")