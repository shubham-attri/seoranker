from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field

class ToneGuidelines(BaseModel):
    do: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)

class StyleGuide(BaseModel):
    writing_style: str = "professional and clear"
    formatting: str = "Use clear paragraphs and headings"
    language: str = "Professional yet accessible"
    key_terms: List[str] = Field(default_factory=list)
    tone_guidelines: Optional[ToneGuidelines] = Field(default_factory=ToneGuidelines)

    def items(self):
        """Make StyleGuide dict-like for compatibility"""
        return {
            "writing_style": self.writing_style,
            "formatting": self.formatting,
            "language": self.language
        }.items()

class BrandStory(BaseModel):
    origin: str = ""
    mission: str = ""
    values: str = ""

class SocialMediaVoice(BaseModel):
    linkedin: str = "Professional and informative"
    twitter: str = "Engaging and concise"
    instagram: str = "Visual and inspiring"

class BrandConfig(BaseModel):
    """Configuration for brand-specific content generation"""
    name: str
    description: str
    tone_of_voice: str = "professional and friendly"
    target_audience: str = "general"
    key_values: List[str] = Field(default_factory=list)
    website: Optional[str] = None
    products: List[Dict[str, str]] = Field(default_factory=list)
    style_guide: StyleGuide = Field(default_factory=StyleGuide)
    brand_story: Optional[BrandStory] = Field(default_factory=BrandStory)
    cta_templates: List[str] = Field(default_factory=list)
    content_themes: List[str] = Field(default_factory=list)
    social_media_voice: Optional[SocialMediaVoice] = Field(default_factory=SocialMediaVoice)
    hashtags: List[str] = Field(default_factory=list)
    
    class Config:
        extra = "allow"  # Allows additional fields 