"""
TESTIMONIAL GENERATOR
=====================
Convert 5-star reviews into social posts.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')

SOCIAL_TEMPLATES = {
    "facebook": "📣 What our customers are saying:\n\n\"{quote}\"\n\n- {name}\n\n{hashtags}\n\n#CustomerLove #5StarService",
    "instagram": "Another happy customer! 🌟\n\n\"{quote}\"\n\n- {name}\n\n{hashtags}",
    "linkedin": "We're grateful for customers like {name}:\n\n\"{quote}\"\n\nThank you for trusting us with your {service} needs.\n\n{hashtags}",
    "twitter": "🌟 \"{quote}\" - {name}\n\nThank you! 🙏 {hashtags}"
}


def generate_testimonial_post(review: dict, platform: str = "facebook") -> dict:
    """Generate social media post from a review"""
    
    # Extract key quote using Grok
    prompt = f"""Extract the best testimonial quote from this review for social media:

Review: {review.get('text', '')}
Rating: {review.get('rating', 5)}/5
Reviewer: {review.get('name', 'Customer')}
Service: {review.get('service', 'our services')}

Return JSON:
{{
    "quote": "The best 1-2 sentence quote (clean it up if needed)",
    "hashtags": ["relevant", "hashtags"],
    "emoji": "one relevant emoji"
}}"""

    quote_data = {"quote": review.get('text', '')[:150], "hashtags": ["#HVAC"], "emoji": "⭐"}
    
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
            quote_data = json.loads(response.json()['choices'][0]['message']['content'])
    except:
        pass
    
    # Format for platform
    template = SOCIAL_TEMPLATES.get(platform, SOCIAL_TEMPLATES["facebook"])
    hashtags = " ".join([f"#{h.replace('#', '')}" for h in quote_data.get('hashtags', [])])
    
    post = template.format(
        quote=quote_data.get('quote', review.get('text', '')[:150]),
        name=review.get('name', 'A Happy Customer'),
        service=review.get('service', 'our services'),
        hashtags=hashtags
    )
    
    return {
        "platform": platform,
        "post": post,
        "original_review": review,
        "generated_at": datetime.now().isoformat()
    }


def batch_generate_testimonials(reviews: list) -> dict:
    """Generate testimonials for multiple platforms from reviews"""
    
    all_posts = {}
    
    for review in reviews:
        if review.get('rating', 0) >= 4:  # Only 4-5 star reviews
            review_posts = {}
            for platform in SOCIAL_TEMPLATES.keys():
                post = generate_testimonial_post(review, platform)
                review_posts[platform] = post['post']
            
            all_posts[review.get('name', 'Customer')] = review_posts
    
    return all_posts


if __name__ == "__main__":
    test_review = {
        "rating": 5,
        "name": "John D.",
        "text": "Amazing service! The tech arrived on time, was super professional, and fixed our AC in under an hour. Will definitely use again!",
        "service": "AC repair"
    }
    
    for platform in ["facebook", "instagram", "twitter"]:
        post = generate_testimonial_post(test_review, platform)
        print(f"\n--- {platform.upper()} ---")
        print(post['post'])
