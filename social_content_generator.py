"""
Social Media Content Generator
AI-powered content creation for HVAC industry
"""

import os
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

CONTENT_THEMES = {
    "hvac_tips": [
        "Energy saving tips",
        "Maintenance best practices",
        "Seasonal HVAC advice",
        "Indoor air quality",
        "Common HVAC problems"
    ],
    "business_insights": [
        "Industry trends",
        "Technology updates",
        "Customer service tips",
        "Business growth strategies",
        "Team management"
    ],
    "success_stories": [
        "Customer testimonials",
        "Project showcases",
        "Before/after transformations",
        "Problem-solving examples"
    ]
}

PLATFORM_SPECS = {
    "linkedin": {
        "max_length": 3000,
        "tone": "professional",
        "hashtags": 5,
        "best_times": ["8:00", "12:00", "17:00"]
    },
    "facebook": {
        "max_length": 500,
        "tone": "friendly",
        "hashtags": 3,
        "best_times": ["9:00", "13:00", "19:00"]
    },
    "twitter": {
        "max_length": 280,
        "tone": "concise",
        "hashtags": 2,
        "best_times": ["9:00", "12:00", "15:00", "18:00"]
    },
    "instagram": {
        "max_length": 2200,
        "tone": "visual",
        "hashtags": 10,
        "best_times": ["11:00", "14:00", "19:00"]
    }
}

def generate_content(theme, platform="linkedin"):
    """
    Generate social media content using Claude AI
    
    Args:
        theme: Content theme (hvac_tips, business_insights, success_stories)
        platform: Target platform (linkedin, facebook, twitter, instagram)
    
    Returns:
        dict with content, hashtags, and metadata
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    platform_spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["linkedin"])
    
    prompt = f"""Create a {platform} post for an HVAC business.

Theme: {theme}
Tone: {platform_spec['tone']}
Max length: {platform_spec['max_length']} characters
Hashtags: {platform_spec['hashtags']}

Requirements:
- Engaging and valuable content
- Industry-specific insights
- Call-to-action
- Professional but approachable
- Include relevant hashtags

Format as JSON:
{{
    "content": "main post text",
    "hashtags": ["hashtag1", "hashtag2"],
    "call_to_action": "CTA text"
}}"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    import json
    content_data = json.loads(message.content[0].text)
    
    # Add metadata
    content_data["platform"] = platform
    content_data["theme"] = theme
    content_data["generated_at"] = datetime.now().isoformat()
    content_data["character_count"] = len(content_data["content"])
    
    return content_data

def generate_daily_content_plan():
    """
    Generate a full day's worth of social media content
    Returns list of posts for different platforms
    """
    posts = []
    
    # Morning post - LinkedIn (HVAC tip)
    posts.append({
        "time": "08:00",
        "platform": "linkedin",
        "content": generate_content("hvac_tips", "linkedin")
    })
    
    # Mid-day post - Facebook (Business insight)
    posts.append({
        "time": "13:00",
        "platform": "facebook",
        "content": generate_content("business_insights", "facebook")
    })
    
    # Afternoon post - Twitter (Quick tip)
    posts.append({
        "time": "15:00",
        "platform": "twitter",
        "content": generate_content("hvac_tips", "twitter")
    })
    
    # Evening post - Instagram (Visual/success story)
    posts.append({
        "time": "19:00",
        "platform": "instagram",
        "content": generate_content("success_stories", "instagram")
    })
    
    return posts

if __name__ == "__main__":
    print("Generating daily social media content...\n")
    
    posts = generate_daily_content_plan()
    
    for post in posts:
        print(f"\n{'='*70}")
        print(f"Time: {post['time']} | Platform: {post['platform'].upper()}")
        print(f"{'='*70}")
        print(f"\nContent:\n{post['content']['content']}")
        print(f"\nHashtags: {' '.join(['#' + h for h in post['content']['hashtags']])}")
        print(f"CTA: {post['content']['call_to_action']}")
        print(f"Characters: {post['content']['character_count']}")
