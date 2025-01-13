from string import Template

class BlogPromptTemplate:
    """Blog generation prompt template"""
    
    @staticmethod
    def get_template() -> str:
        return """
Generate a comprehensive, SEO-optimized blog post about ${keyword}.

Reference Article Analysis:
${h2_analysis}

Suggested H2 Structure:
Create 2-3 H2 sections based on the reference articles above, but ensure they:
1. Follow our brand voice and premium positioning
2. Include at least one section about quality/premium aspects
3. Include "The Bestia Brisk Difference" section
4. Focus on topics that resonate with ambitious professionals

Brand Voice Requirements:
- Bold and confident tone that appeals to ambitious, driven individuals
- We source the finest coffee for you. That's our promise. This is our tag line.
- Focus on premium quality and luxury coffee experience
- Emphasize the unique blend of 60% Arabica, 40% Robusta from Coorg
- Highlight AAA grade beans and small-batch production
- Target audience: Young professionals, entrepreneurs, and coffee enthusiasts
- Use phrases like "bold", "premium", "luxury", "elevate your coffee experience"
- Maintain a balance between expert knowledge and accessible language

Content Structure:
1. Introduction:
   - Hook with a bold statement about ${keyword}
   - Establish authority and premium positioning
   - Preview the value for ambitious professionals

2. Main Sections (Use 2-3 H2s based on analysis above):
   - Each section should flow naturally
   - Include expert insights
   - Reference scientific/industry sources
   - Connect to reader's aspirations

3. The Bestia Brisk Difference:
   - Our commitment to AAA grade beans
   - Artisanal small-batch production
   - Perfect blend ratio (60% Arabica, 40% Robusta)
   - Premium instant coffee convenience

4. Conclusion:
   - Reinforce premium positioning
   - Strong call-to-action
   - Link to product page

HTML Format Requirements:
- Use one <h1> tag for the main title
- Use 2-3 <h2> tags for main sections (based on analysis)
- Use <h3> tags for subsections
- Use <p> tags for paragraphs
- Use <ul> and <li> tags for lists
- Use proper <a> tags for links with target="_blank"

Content Requirements:
1. Include these product references naturally:
${product_info}

2. Address these customer questions:
${questions}

3. Include these internal blog links in relevant contexts:
${internal_links}

4. Use these sources for research:
${sources}

SEO Requirements:
- Primary keyword: ${keyword}
- Include keyword naturally throughout content
- Include the internal blog links provided above
- Include 2-3 external authority links (only for scientific/educational content)
- Minimum length: 2000 words
- Include meta description (155 characters)

Remember to:
1. Analyze and incorporate successful elements from reference articles
2. Maintain consistent premium positioning
3. Focus on value for ambitious professionals
4. Naturally integrate Bestia Brisk's unique selling points
"""

    @staticmethod
    def format_prompt(
        keyword: str,
        h2_analysis: str,
        product_info: str,
        questions: str,
        internal_links: str,
        sources: str
    ) -> str:
        """Format prompt template with provided values"""
        template = Template(BlogPromptTemplate.get_template())
        return template.safe_substitute(
            keyword=keyword,
            h2_analysis=h2_analysis,
            product_info=product_info,
            questions=questions,
            internal_links=internal_links,
            sources=sources
        ) 