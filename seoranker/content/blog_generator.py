from typing import Dict, List, Optional
from pathlib import Path
import csv
import json
from groq import Groq
from seoranker.utils.logger import setup_logger
from seoranker.config.settings import GROQ_API_KEY
from seoranker.content.content_archive import ContentArchive
from datetime import datetime
from seoranker.llm.anthropic_llm import AnthropicLLM
from seoranker.llm.groq_llm import GroqLLM
import re
from seoranker.content.social_generator import SocialGenerator
from seoranker.config.model_config import ModelConfig, TaskType
from seoranker.llm.model_factory import ModelFactory
from seoranker.templates.blog_prompt import BlogPromptTemplate

logger = setup_logger(__name__)

class BlogGenerator:
    """Generate SEO-optimized blog content for Shopify"""
    
    def __init__(self):
        config = ModelConfig()
        blog_config = config.get_model_config(TaskType.BLOG)
        self.blog_llm = ModelFactory.create_llm(blog_config)
        self.social_llm = GroqLLM()     # Use Groq for social content
        self.groq = Groq(api_key=GROQ_API_KEY)
        self.content_db_path = Path("knowledge_base/content_database.csv")
        self.suggestions_db_path = Path("knowledge_base/suggestions_database.csv")
        self.product_db_path = Path("knowledge_base/products.json")
        self.content_archive = ContentArchive()
        self.blog_archive_path = self.content_archive.blog_archive_path
        self.social_archive_path = self.content_archive.social_archive_path
        self.social_generator = SocialGenerator()
        
    def _load_reference_content(self, keyword: str) -> Dict:
        """Load relevant content from databases"""
        content = {
            "main_sources": [],
            "questions": [],
            "related_blogs": [],
            "products": []
        }
        
        try:
            # Get top 3 reference articles
            with open(self.content_db_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['keyword'].lower() == keyword.lower():
                        content["main_sources"].append({
                            "url": row["url"],
                            "title": row["title"],
                            "content": row["content"]
                        })
                        if len(content["main_sources"]) >= 3:
                            break
            
            # Get relevant questions
            with open(self.suggestions_db_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['source_keyword'].lower() == keyword.lower():
                        content["questions"].append({
                            "question": row["question"],
                            "title": row["title"],
                            "url": row["url"]
                        })
            
            # Get related blog posts using ContentArchive
            related = self.content_archive.get_related_content(keyword, limit=3)
            content["related_blogs"] = related.get("blogs", [])
            
            # Get relevant products
            if self.product_db_path.exists():
                with open(self.product_db_path, 'r', encoding='utf-8') as f:
                    products = json.load(f)
                    content["products"] = products.get("products", [])
                
            return content
            
        except Exception as e:
            logger.error(f"Error loading reference content: {str(e)}")
            return content  # Return empty content structure on error
    
    def _generate_blog_prompt(self, keyword: str, content: Dict) -> str:
        """Create detailed prompt for blog generation"""
        # Get relevant internal links
        internal_links = self._get_relevant_internal_links(keyword)
        
        # Extract H2 structure from reference articles
        h2_analysis = "Reference Article Structures:\n"
        for idx, source in enumerate(content["main_sources"], 1):
            article_content = source.get("content", "")
            h2_tags = re.findall(r'<h2[^>]*>(.*?)</h2>', article_content, re.IGNORECASE | re.DOTALL)
            if h2_tags:
                h2_analysis += f"\nArticle {idx} Structure:\n"
                for h2 in h2_tags:
                    h2_analysis += f"- {h2.strip()}\n"
        
        # Add Bestia Brisk product info
        bestia_product = {
            "name": "Bestia Brisk Original Instant Coffee",
            "url": "https://bestiabrisk.com/products/bestia-brisk-original-instant-coffee",
            "details": {
                "origin": "Coorg (Single Origin)",
                "grade": "AAA",
                "blend": "60% Arabica, 40% Robusta",
                "roast": "Light Roast (Slow Roasted)",
                "production": "Small Batch",
                "type": "Instant Coffee (Granule)"
            }
        }
        
        return BlogPromptTemplate.format_prompt(
            keyword=keyword,
            h2_analysis=h2_analysis,
            product_info=json.dumps([bestia_product], indent=2),
            questions=json.dumps(content["questions"], indent=2),
            internal_links=json.dumps(internal_links["relevant_links"], indent=2),
            sources=json.dumps(content["main_sources"], indent=2)
        )

    def _extract_metadata(self, content: str) -> Dict:
        """Extract metadata and content from Claude's response"""
        try:
            logger.debug("\nExtracting metadata and content...")
            
            # Extract metadata section
            metadata_match = re.search(r'<metadata>(.*?)</metadata>', content, re.DOTALL)
            if not metadata_match:
                logger.error("No metadata section found")
                return {}
            
            metadata_text = metadata_match.group(1)
            
            # Parse title and meta description
            title_match = re.search(r'title:\s*(.*?)(?:\n|$)', metadata_text)
            meta_desc_match = re.search(r'meta_description:\s*(.*?)(?:\n|$)', metadata_text)
            
            # Extract main content - everything between <content> tags
            content_match = re.search(r'<content>\s*(.*?)\s*</content>', content, re.DOTALL)
            if not content_match:
                logger.error("No content section found")
                return {}
            
            blog_content = content_match.group(1).strip()
            
            # Remove any suggested image placements or other sections after </content>
            blog_content = blog_content.split('Suggested Image Placements')[0].strip()
            
            metadata = {
                "title": title_match.group(1).strip() if title_match else "",
                "meta_description": meta_desc_match.group(1).strip() if meta_desc_match else "",
                "blog_content": blog_content  # Changed from html_content to blog_content
            }
            
            logger.debug("\nExtracted Content:")
            logger.debug(f"- Title: {metadata['title']}")
            logger.debug(f"- Meta Description: {metadata['meta_description']}")
            logger.debug(f"- Content Length: {len(blog_content)} chars")
            logger.debug(f"- First 200 chars of content:\n{blog_content[:200]}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {}

    def _validate_content(self, content: Dict) -> bool:
        """Validate generated content meets requirements"""
        try:
            blog_content = content.get("blog_content", "").strip()
            logger.debug("\nValidating Content:")
            logger.debug(f"- Content length: {len(blog_content)} chars")
            
            # Basic validation
            if not blog_content:
                logger.error("No blog content found")
                return False
            
            # Word count check
            word_count = len(blog_content.split())
            logger.debug(f"- Word count: {word_count}")
            if word_count < 500:
                logger.error(f"Content too short: {word_count} words")
                return False
            
            # Structure validation
            h1_count = blog_content.lower().count("<h1")
            h2_count = blog_content.lower().count("<h2")
            logger.debug(f"- H1 tags: {h1_count}")
            logger.debug(f"- H2 tags: {h2_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating content: {str(e)}")
            return False

    def _save_content_files(self, keyword: str, content: Dict) -> Dict:
        """Save content to files"""
        try:
            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            # Sanitize keyword for filename
            safe_keyword = "".join(c if c.isalnum() else "_" for c in keyword.lower())
            blog_file = output_dir / f"{safe_keyword}.html"
            
            # Generate complete HTML
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="description" content="{content['meta_description']}">
    <title>{content['title']}</title>
</head>
<body>
    {content['blog_content']}
</body>
</html>"""
            
            # Save HTML file
            with open(blog_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.debug(f"✓ Saved blog post to: {blog_file}")
            
            # Generate social content versions
            social_content = self.social_generator.generate_all(content)
            
            return {
                "blog": str(blog_file.absolute()),  # Use absolute path
                "linkedin": social_content.get("linkedin", ""),
                "twitter": social_content.get("twitter", ""),
                "status": "draft"
            }
            
        except Exception as e:
            logger.error(f"Error saving content files: {str(e)}")
            return None

    def generate_blog(self, keyword: str) -> Dict:
        """Generate complete blog post"""
        try:
            logger.debug(f"\n{'='*50}")
            logger.debug(f"Starting blog generation for: {keyword}")
            logger.debug(f"{'='*50}")
            
            # 1. Load reference content
            logger.debug("\n1. LOADING REFERENCE CONTENT")
            logger.debug("-" * 30)
            content = self._load_reference_content(keyword)
            
            # Debug content sources
            logger.debug("\nMain Sources:")
            for src in content["main_sources"]:
                logger.debug(f"- {src['title']}")
                logger.debug(f"  URL: {src['url']}")
            
            logger.debug("\nQuestions to Address:")
            for q in content["questions"]:
                logger.debug(f"- {q['question']}")
            
            logger.debug("\nRelated Blogs:")
            for blog in content["related_blogs"]:
                logger.debug(f"- {blog.get('title', 'No title')}")
            
            logger.debug("\nProducts to Reference:")
            for product in content["products"]:
                logger.debug(f"- {product.get('name', 'No name')}")
            
            # 2. Generate prompt
            logger.debug("\n2. GENERATING PROMPT")
            logger.debug("-" * 30)
            prompt = self._generate_blog_prompt(keyword, content)
            logger.debug("\nPrompt Structure:")
            logger.debug(f"- Total length: {len(prompt)} chars")
            logger.debug(f"- Keyword: {keyword}")
            logger.debug(f"- Sources: {len(content['main_sources'])}")
            logger.debug(f"- Questions: {len(content['questions'])}")
            logger.debug(f"- Products: {len(content['products'])}")
            logger.debug("\nFull Prompt:")
            logger.debug(f"{prompt}")
            
            # 3. Generate content
            logger.debug("\n3. GENERATING CONTENT")
            logger.debug("-" * 30)
            logger.debug(f"Using model: {self.blog_llm.get_model_name()}")
            logger.debug(f"Max tokens: {self.blog_llm.max_tokens_limit}")
            
            blog_content = self.blog_llm.generate_content(prompt)
            
            # Debug generated content
            logger.debug("\nGenerated Content:")
            logger.debug(f"- Length: {len(blog_content)} chars")
            logger.debug("- First 200 chars:")
            logger.debug(blog_content)
            
            # 4. Extract metadata
            logger.debug("\n4. EXTRACTING METADATA")
            logger.debug("-" * 30)
            metadata = self._extract_metadata(blog_content)
            logger.debug("Extracted Metadata:")
            logger.debug(f"- Title: {metadata.get('title', 'No title')}")
            logger.debug(f"- Meta Description: {metadata.get('meta_description', 'No meta')}")
            logger.debug(f"- HTML Content Length: {len(metadata.get('html_content', ''))}")
            
            # Structure content
            content_dict = {
                "blog_content": metadata["blog_content"],
                "meta_description": metadata["meta_description"],
                "title": metadata["title"],
                "internal_links": [],
                "external_links": []
            }
            
            # 5. Validate content
            logger.debug("\n5. VALIDATING CONTENT")
            logger.debug("-" * 30)
            validation_result = self._validate_content(content_dict)
            logger.debug(f"Validation Result: {'✓ Passed' if validation_result else '✗ Failed'}")
            
            if not validation_result:
                raise ValueError("Generated content failed validation")
            
            # Save content files
            logger.debug("\n6. SAVING CONTENT FILES")
            logger.debug("-" * 30)
            saved_files = self._save_content_files(keyword, content_dict)
            
            # Save to archive
            logger.debug("\n7. SAVING TO ARCHIVE")
            logger.debug("-" * 30)
            content_dict.update({
                "linkedin_content": saved_files.get("linkedin"),
                "twitter_thread": saved_files.get("twitter")
            })
            archive_result = self._save_to_archive(keyword, content_dict)
            logger.debug(f"✓ Archive save result: {archive_result}")
            
            return {
                "keyword": keyword,
                "content": content_dict,
                "status": "success",
                "blog_id": archive_result.get("blog_id"),
                "files": saved_files
            }
            
        except Exception as e:
            logger.error(f"Error generating blog: {str(e)}", exc_info=True)
            return {
                "keyword": keyword,
                "error": str(e),
                "status": "failed"
            }

    def _save_to_archive(self, keyword: str, content: Dict) -> Dict:
        """Save generated content to archives"""
        try:
            logger.debug(f"\nSaving to archive:")
            logger.debug(f"- Keyword: {keyword}")
            logger.debug(f"- Title: {content['title']}")
            
            # Add file paths and metadata
            archive_content = {
                "keyword": keyword,
                "title": content["title"],
                "meta_description": content["meta_description"],
                "file_path": content.get("files", {}).get("blog", ""),
                "created_at": datetime.now().isoformat()
            }
            
            return self.content_archive.save_content(archive_content)
            
        except Exception as e:
            logger.error(f"Error saving to archive: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 

    def _get_relevant_internal_links(self, keyword: str) -> Dict:
        """Get relevant internal links using Groq LLM"""
        try:
            # Get existing blog posts from archive
            with open(self.blog_archive_path, 'r') as f:
                archive = json.load(f)
                existing_blogs = archive.get("blogs", [])
            
            # Create prompt for Groq
            prompt = f"""
Given the keyword "{keyword}", analyze these blog posts and return the 3 most relevant ones 
that should be linked in our new blog post about {keyword}.

Blog Posts:
{json.dumps([{
    'title': blog['title'],
    'description': blog['meta_description'],
    'path': blog['file_path']
} for blog in existing_blogs], indent=2)}

Return only the JSON response in this format:
{{
    "relevant_links": [
        {{
            "title": "Blog post title",
            "path": "file path",
            "context": "Suggested context for linking (1 sentence)"
        }}
    ]
}}
"""
            # Use Groq for quick analysis
            response = self.social_llm.generate_content(prompt)
            relevant_links = json.loads(response)
            
            logger.debug("\nRelevant Internal Links:")
            for link in relevant_links["relevant_links"]:
                logger.debug(f"- {link['title']}")
                logger.debug(f"  Context: {link['context']}")
            
            return relevant_links
            
        except Exception as e:
            logger.error(f"Error getting relevant links: {str(e)}")
            return {"relevant_links": []} 