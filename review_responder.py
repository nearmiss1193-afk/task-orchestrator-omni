"""
REVIEW RESPONDER
================
AI auto-responds to Google/Yelp reviews (good & bad).
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')

RESPONSE_TEMPLATES = {
    "5_star": "Thank you so much for the amazing review, {name}! We're thrilled you had a great experience. Your recommendation means the world to us!",
    "4_star": "Thanks for the great feedback, {name}! We're glad you had a positive experience. If there's anything we can do better, we'd love to hear!",
    "3_star": "Hi {name}, thanks for taking the time to review us. We'd love to hear how we can improve - please reach out directly!",
    "2_star": "Hi {name}, we're sorry your experience didn't meet expectations. We'd like to make this right - please contact us directly.",
    "1_star": "{name}, we sincerely apologize for your experience. This isn't our standard. Please call us at {phone} so we can resolve this immediately."
}


def generate_response(review: dict) -> str:
    """Generate personalized response using Grok"""
    
    rating = review.get('rating', 3)
    reviewer_name = review.get('reviewer_name', 'there')
    review_text = review.get('text', '')
    business_name = review.get('business_name', 'our team')
    
    prompt = f"""Generate a professional, warm response to this review:

Rating: {rating}/5 stars
Reviewer: {reviewer_name}
Review: {review_text}
Business: {business_name}

Guidelines:
- Be genuine and personalized (reference specifics from their review)
- For negative reviews: apologize, take responsibility, offer to make it right
- For positive reviews: express gratitude, encourage referrals
- Keep it under 100 words
- Sign off with the owner's name

Return just the response text, no JSON."""

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-3-mini",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"[ERROR] Grok failed: {e}")
    
    # Fallback to template
    template_key = f"{min(max(rating, 1), 5)}_star"
    return RESPONSE_TEMPLATES.get(template_key, RESPONSE_TEMPLATES["3_star"]).format(
        name=reviewer_name, phone="+1 (863) 213-2505"
    )


def process_reviews(reviews: list) -> list:
    """Process batch of reviews and generate responses"""
    results = []
    for review in reviews:
        response = generate_response(review)
        results.append({
            "review": review,
            "response": response,
            "generated_at": datetime.now().isoformat()
        })
        print(f"[REVIEW] {review.get('rating')}★ from {review.get('reviewer_name')} - Response generated")
    return results


if __name__ == "__main__":
    # Test
    test_reviews = [
        {"rating": 5, "reviewer_name": "John D.", "text": "Amazing service! Tech arrived on time and fixed our AC in under an hour.", "business_name": "Cool Breeze HVAC"},
        {"rating": 2, "reviewer_name": "Sarah M.", "text": "Waited 3 hours for tech to show up. Not happy.", "business_name": "Cool Breeze HVAC"},
    ]
    
    results = process_reviews(test_reviews)
    for r in results:
        print(f"\n--- {r['review']['reviewer_name']} ({r['review']['rating']}★) ---")
        print(r['response'])
