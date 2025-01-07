from typing import Dict
from seoranker.config.model_config import ModelConfig, TaskType
from seoranker.llm.model_factory import ModelFactory
from seoranker.utils.logger import setup_logger

logger = setup_logger(__name__)

class SocialGenerator:
    """Generate social media content from blog posts"""
    
    def __init__(self):
        config = ModelConfig()
        social_config = config.get_model_config(TaskType.SOCIAL)
        self.llm = ModelFactory.create_llm(social_config)
    
    def generate_linkedin_post(self, blog_content: Dict) -> str:
        """Generate LinkedIn post from blog content"""
        try:
            prompt = f"""
Create a professional LinkedIn post about this blog post.

Blog Details:
- Title: {blog_content['title']}
- Topic: {blog_content['meta_description']}

Brand Voice:
- Professional and confident
- Target audience: Ambitious professionals and coffee enthusiasts
- Focus on premium quality and luxury experience
- Highlight Bestia Brisk's unique value proposition

Requirements:
- Professional tone
- 1-2 engaging paragraphs
- Include 2-3 relevant hashtags (e.g., #PremiumCoffee #BestiaBrisk #LuxuryCoffee)
- Include link to blog
- Max 1300 characters
- End with a clear call-to-action

Example Format:
[Hook/Opening]
[Main Value Proposition]
[Call-to-Action]
[Link]
[Hashtags]
"""
            return self.llm.generate_content(prompt)
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn post: {str(e)}")
            return ""
    
    def generate_twitter_thread(self, blog_content: Dict) -> str:
        """Generate Twitter thread from blog content"""
        try:
            prompt = f"""
Create an engaging Twitter thread about this blog post.

Blog Details:
- Title: {blog_content['title']}
- Topic: {blog_content['meta_description']}

Brand Voice:
- Bold and confident
- Educational yet accessible
- Premium positioning
- Focus on quality and expertise

Requirements:
- 5-7 tweets total
- Each tweet max 280 chars
- Number format: [1/5] [Tweet content]
- Include relevant hashtags
- Include link to blog in last tweet
- Mix of education and value proposition
- End with strong call-to-action

Example Structure:
[1/5] Hook + Problem
[2/5] Key Insight/Fact
[3/5] Unique Value Proposition
[4/5] Expert Tip/Benefit
[5/5] CTA + Link
"""
            return self.llm.generate_content(prompt)
            
        except Exception as e:
            logger.error(f"Error generating Twitter thread: {str(e)}")
            return ""
    
    def generate_all(self, blog_content: Dict) -> Dict:
        """Generate all social media versions"""
        try:
            logger.debug("\nGenerating social media content:")
            logger.debug(f"- Blog title: {blog_content['title']}")
            
            # Generate LinkedIn post
            logger.debug("Generating LinkedIn post...")
            linkedin_content = self.generate_linkedin_post(blog_content)
            
            # Generate Twitter thread
            logger.debug("Generating Twitter thread...")
            twitter_content = self.generate_twitter_thread(blog_content)
            
            return {
                "linkedin": linkedin_content,
                "twitter": twitter_content
            }
            
        except Exception as e:
            logger.error(f"Error generating social content: {str(e)}")
            return {} 