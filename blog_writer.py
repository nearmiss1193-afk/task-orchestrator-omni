"""
BLOG WRITER
===========
Weekly SEO blog from Sarah call FAQs.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')


def extract_faqs_from_calls(call_transcripts: list) -> list:
    """Extract common FAQs from call transcripts"""
    
    all_text = "\n\n".join([t.get('transcript', '') for t in call_transcripts])
    
    prompt = f"""Analyze these service call transcripts and extract the most common customer questions:

Transcripts:
{all_text[:8000]}

Return JSON:
{{
    "faqs": [
        {{"question": "Common question", "frequency": "how often asked", "answer_summary": "brief answer"}}
    ],
    "trending_topics": ["topic1", "topic2"]
}}"""

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return json.loads(response.json()['choices'][0]['message']['content'])
    except:
        pass
    
    return {"faqs": [], "trending_topics": []}


def generate_blog_post(topic: str, industry: str = "HVAC") -> dict:
    """Generate SEO-optimized blog post"""
    
    prompt = f"""Write an SEO-optimized blog post for a {industry} company:

Topic: {topic}

Requirements:
- 600-800 words
- Include H2 subheadings
- Natural keyword placement
- Helpful, actionable content
- End with a call to action

Format as HTML with proper tags (<h1>, <h2>, <p>, <ul>, etc.)"""

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            
            return {
                "topic": topic,
                "industry": industry,
                "content_html": content,
                "word_count": len(content.split()),
                "generated_at": datetime.now().isoformat(),
                "seo_keywords": extract_keywords(topic, industry)
            }
    except Exception as e:
        print(f"[ERROR] Blog generation failed: {e}")
    
    return {"error": "Generation failed"}


def extract_keywords(topic: str, industry: str) -> list:
    """Extract SEO keywords from topic"""
    keywords = [
        industry.lower(),
        topic.lower(),
        f"{industry.lower()} services",
        f"{industry.lower()} near me",
        f"best {industry.lower()}"
    ]
    return keywords


def save_blog_post(post: dict):
    """Save blog post to file"""
    os.makedirs("blog_posts", exist_ok=True)
    
    filename = f"blog_posts/{datetime.now().strftime('%Y%m%d')}_{post['topic'][:30].replace(' ', '_')}.html"
    
    with open(filename, "w", encoding='utf-8') as f:
        f.write(post['content_html'])
    
    print(f"[BLOG] Saved: {filename}")
    return filename


def generate_weekly_content(industry: str = "HVAC") -> list:
    """Generate a week's worth of blog content"""
    
    topics = [
        f"5 Signs Your {industry} System Needs Repair",
        f"How to Save Money on {industry} Bills This Season",
        f"Common {industry} Problems and How to Fix Them",
        f"When to Replace vs Repair Your {industry} System",
        f"DIY {industry} Maintenance Tips for Homeowners"
    ]
    
    posts = []
    for topic in topics[:3]:  # Generate 3 to avoid timeouts
        print(f"[BLOG] Generating: {topic}")
        post = generate_blog_post(topic, industry)
        if 'error' not in post:
            posts.append(post)
            save_blog_post(post)
    
    return posts


if __name__ == "__main__":
    # Test single blog
    post = generate_blog_post("5 Signs Your AC Needs Repair This Summer", "HVAC")
    
    if 'error' not in post:
        print(f"Generated: {post['topic']} ({post['word_count']} words)")
        save_blog_post(post)
