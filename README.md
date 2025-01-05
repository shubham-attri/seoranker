# SEO Content Generator with Brand Voice Integration

A powerful AI-driven content generation system that creates SEO-optimized blog posts and social media content while maintaining consistent brand voice. Built with LangChain and Anthropic's Claude.

## Overview

This system generates multiple variations of SEO-optimized content for given topics while maintaining your brand's voice and style. It uses AI to:

1. Research competitor content using Exa AI
2. Generate unique blog posts with different angles
3. Create matching social media content
4. Maintain brand voice consistency
5. Follow SEO best practices

## Features

### Content Generation
- Multiple variations per topic (recommended: 5)
- Different focus angles for each variation:
  - Beginner's guide and fundamentals
  - Advanced techniques and expert tips
  - Latest trends and innovations
  - Practical applications
  - Deep-dive analysis

### Brand Voice Integration
- Customizable brand configuration
- Tone and style guidelines
- Product integration
- Call-to-action templates
- Content themes
- Social media voice adaptation

### Output Types
For each variation, generates:
- SEO-optimized blog post (1500-2000 words)
- LinkedIn post (1300 characters)
- Twitter thread (5-7 tweets)
- Relevant hashtags

### Content Organization
Generated content is automatically organized:

```
generated_content/
├── keyword_v1_20241229_234832/      # Timestamp-based directories
│   ├── seo-optimized-blog-title.md   # Main blog post
│   ├── linkedin_post.md              # LinkedIn content
│   ├── twitter_thread.md             # Twitter thread
│   ├── hashtags.md                   # Relevant hashtags
│   └── metadata.json                 # Content metadata
└── keyword_v2_20241229_234057/
    └── ...

knowledge_base/                       # Research data storage
└── keyword/
    ├── 20241229_234832_source1.md   # Competitor research
    ├── 20241229_234832_source2.md   # Market insights
    └── 20241229_234832_metadata.json # Research metadata
```

## Setup & Installation

1. Clone the repository
2. Install dependencies:
```bash
./setup.sh
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys:
# ANTHROPIC_API_KEY=your_key
# EXA_API_KEY=your_key
```

## Usage

1. Configure your brand voice in `config/brand.json`:
```json
{
  "name": "Bestia Brisk",
  "description": "Bestia Brisk is a premium coffee blend that combines the rich flavors of Arabica beans with the robust taste of Robusta beans. It's a smooth and balanced blend that's perfect for any time of day.",
  "tone_of_voice": "professional, friendly, and authoritative, with a focus on coffee expertise and authenticity",
  "target_audience": "coffee enthusiasts aged 25-45 who appreciate premium, artisanal coffee",
  "key_values": [
    "Premium Quality",
    "Artisanal Craftsmanship",
    "Sustainable Sourcing",
    "Single Origin Excellence",
    "Small Batch Production"
  ],
  "website": "https://bestiabrisk.com/",
  "products": [
    {
      "name": "Bestia Brisk Original",
      "description": "A premium single-origin coffee from Coorg, featuring:\n- AAA Grade beans\n- Perfect blend of 60% Arabica and 40% Robusta\n- Light roasted using slow-roasting technique\n- Small-batch production for quality control\n- Premium instant coffee granules"
    }
  ],
  "style_guide": {
    "writing_style": "Expert yet approachable, focusing on coffee craftsmanship and quality",
    "formatting": "Use short, engaging paragraphs with clear headings and bullet points",
    "language": "Use coffee industry terminology while remaining accessible to enthusiasts",
    "key_terms": [
      "single-origin",
      "artisanal",
      "slow-roasted",
      "small-batch",
      "premium blend",
      "Coorg coffee",
      "light roast"
    ],
    "tone_guidelines": {
      "do": [
        "Emphasize quality and craftsmanship",
        "Share coffee expertise confidently",
        "Be transparent about sourcing and process",
        "Use sensory descriptions"
      ],
      "avoid": [
        "Overly technical jargon",
        "Generic coffee descriptions",
        "Pushy sales language"
      ]
    }
  },
  "brand_story": {
    "origin": "Crafted in the lush coffee plantations of Coorg",
    "mission": "To deliver premium, single-origin coffee experiences through artisanal craftsmanship",
    "values": "We believe in sustainable sourcing, small-batch excellence, and preserving coffee's authentic flavors"
  },
  "cta_templates": [
    "Experience the artisanal excellence of {brand_name}",
    "Discover our premium Coorg coffee blend",
    "Elevate your coffee experience with {product_name}",
    "Taste the difference of small-batch craftsmanship",
    "Begin your premium coffee journey today"
  ],
  "content_themes": [
    "Coffee craftsmanship and expertise",
    "Single-origin coffee education",
    "Sustainable coffee production",
    "Artisanal roasting techniques",
    "Coffee tasting and appreciation",
    "Coorg coffee heritage"
  ],
  "social_media_voice": {
    "linkedin": "Professional yet passionate about coffee craft",
    "twitter": "Engaging coffee expertise with personality",
    "instagram": "Visual storytelling of our coffee journey"
  },
  "hashtags": [
    "#BestiaBrisk",
    "#PremiumCoffee",
    "#SingleOrigin",
    "#CoorgCoffee",
    "#ArtisanalCoffee",
    "#CoffeeCraft",
    "#SmallBatchCoffee"
  ]
}
```

This configuration helps maintain consistent brand voice across all generated content, ensuring:
- Coffee expertise shines through
- Premium positioning is maintained
- Brand story is woven naturally
- Product features are highlighted appropriately
- Social media content matches platform expectations

2. Run the content generator:
```bash
./run.sh
```

3. Follow the interactive prompts:
```
How many topics would you like to write about? [Enter number]
How many variations per topic? (recommended: 5) [Enter number]
Enter topic #1 for article generation: [Your keyword]
```

### Generated Output Structure

Each generated article directory contains:

1. **Blog Post (`seo-optimized-title.md`)**
   ```markdown
   # SEO Optimized Title
   
   Meta description: Engaging 155-character description
   
   ## Introduction
   Hook and context...
   
   ## Main Sections
   Content organized with H2 and H3...
   
   ## Conclusion
   Call-to-action
   ```

2. **LinkedIn Post (`linkedin_post.md`)**
   ```markdown
   # LinkedIn Post
   
   Professional, insight-rich content optimized for LinkedIn's format...
   ```

3. **Twitter Thread (`twitter_thread.md`)**
   ```markdown
   # Twitter Thread
   
   1/7 Opening tweet with hook...
   2/7 Key point one...
   [...]
   7/7 Conclusion with CTA
   ```

4. **Metadata (`metadata.json`)**
   ```json
   {
     "title": "Article Title",
     "keyword": "target_keyword",
     "timestamp": "20241229_234832",
     "files": {
       "blog": "path/to/blog.md",
       "linkedin": "path/to/linkedin.md",
       "twitter": "path/to/twitter.md",
       "hashtags": "path/to/hashtags.md"
     },
     "content_stats": {
       "blog_length": 1500,
       "linkedin_length": 1300,
       "twitter_thread_length": 7,
       "hashtags_count": 10
     }
   }
   ```

## Features in Detail

### Research Integration
- Uses Exa AI for competitor content analysis
- Stores research in knowledge base
- Analyzes top-performing content
- Identifies key topics and patterns

### Brand Voice Consistency
- Maintains tone across all content types
- Integrates brand values and messaging
- Uses brand-specific CTAs
- Includes product references naturally

### SEO Optimization
- Keyword optimization
- Meta description generation
- Header structure
- Internal linking suggestions
- Featured snippet optimization

## Error Handling

The system includes robust error handling:
- Continues processing remaining articles if one fails
- Provides detailed error logs
- Creates error reports in metadata
- Maintains partial results

## Logging

Detailed logging is available at multiple levels:
- Generation progress
- Content statistics
- Error tracking
- Performance metrics

## Requirements
- Python 3.8+
- Anthropic API key
- Exa AI API key
- Poetry for dependency management 


'''
Should only have one H1 tag, that is our heading, title, and should have 2-3 h2 tags supporting the targetted keyword, and then the page should link to atleast 2 pages in our website and 2 external website 
'''


How to create a blog article in shopify

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