"""
VIDEO PERSONALIZATION
=====================
Generate personalized AI videos for prospects using Grok.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')


def generate_video_script(prospect: dict, template: str = "intro") -> dict:
    """Generate personalized video script using Grok"""
    
    templates = {
        "intro": """Create a 30-second personalized video script for {name} at {company}.

Context:
- Industry: {industry}
- Pain point: Missing calls after hours
- Our solution: 24/7 AI receptionist

The script should:
1. Greet them by name and company
2. Reference their specific industry challenges
3. Highlight ONE key benefit
4. End with a clear CTA (visit our site or call)

Make it conversational and authentic, not salesy.""",
        
        "followup": """Create a 20-second follow-up video script for {name} at {company}.

Context:
- We sent them info {days_ago} days ago
- No response yet
- Industry: {industry}

Keep it friendly, not pushy. Acknowledge they're busy and offer to help when ready.""",
        
        "thank_you": """Create a 15-second thank-you video script for {name} at {company}.

Context:
- They just signed up or showed interest
- Industry: {industry}

Express genuine gratitude and excitement to work with them."""
    }
    
    prompt = templates.get(template, templates["intro"]).format(
        name=prospect.get('name', 'there'),
        company=prospect.get('company', 'your company'),
        industry=prospect.get('industry', 'home services'),
        days_ago=prospect.get('days_ago', 3)
    )
    
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
            script = response.json()['choices'][0]['message']['content']
            return {
                "prospect": prospect,
                "template": template,
                "script": script,
                "generated_at": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"[ERROR] Script generation failed: {e}")
    
    return {"error": "Generation failed"}


def generate_video_thumbnail(prospect: dict) -> dict:
    """Generate video thumbnail concept"""
    
    return {
        "prospect": prospect.get('name'),
        "thumbnail_concept": {
            "text": f"Hey {prospect.get('name', 'there').split()[0]}!",
            "background": "gradient_blue",
            "avatar_position": "right",
            "company_logo": True
        },
        "note": "Use Canva, Figma, or AI image gen to create"
    }


def create_video_campaign(prospects: list) -> list:
    """Create video campaign for multiple prospects"""
    
    results = []
    
    for prospect in prospects:
        script_result = generate_video_script(prospect, "intro")
        thumbnail = generate_video_thumbnail(prospect)
        
        result = {
            "prospect": prospect,
            "script": script_result.get('script', ''),
            "thumbnail": thumbnail,
            "status": "script_ready",
            "next_steps": [
                "Record video using script",
                "Upload to hosting (Loom, YouTube unlisted)",
                "Send personalized email with video link"
            ]
        }
        results.append(result)
        print(f"[VIDEO] Script ready for {prospect.get('name')}")
    
    return results


def send_video_email(prospect: dict, video_url: str, script_preview: str = "") -> dict:
    """Send personalized video email"""
    
    if not RESEND_API_KEY:
        return {"mock": True, "message": "Resend not configured"}
    
    email_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2>Hey {prospect.get('name', 'there').split()[0]}, I made this for you! 👋</h2>
    
    <p>I recorded a quick personal video just for you and {prospect.get('company', 'your team')}.</p>
    
    <div style="margin: 30px 0; text-align: center;">
        <a href="{video_url}" style="display: inline-block; background: #2563eb; color: white; padding: 16px 32px; border-radius: 12px; text-decoration: none; font-weight: bold;">
            ▶️ Watch Your Personal Video
        </a>
    </div>
    
    <p>It's only 30 seconds - I think you'll find it interesting!</p>
    
    <p>Talk soon,<br>
    Sarah<br>
    AI Service Co</p>
    </body>
    </html>
    """
    
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": "Sarah <sarah@aiserviceco.com>",
                "to": [prospect.get('email')],
                "subject": f"Quick video for you, {prospect.get('name', '').split()[0]} 🎬",
                "html": email_html
            }
        )
        return {"sent": response.status_code == 200, "prospect": prospect.get('name')}
    except Exception as e:
        return {"sent": False, "error": str(e)}


def get_video_platforms() -> dict:
    """Get recommended video creation platforms"""
    return {
        "recording": [
            {"name": "Loom", "url": "https://loom.com", "use_case": "Quick screen/face recordings"},
            {"name": "Vidyard", "url": "https://vidyard.com", "use_case": "Sales-focused videos"},
        ],
        "ai_generation": [
            {"name": "HeyGen", "url": "https://heygen.com", "use_case": "AI avatar videos"},
            {"name": "Synthesia", "url": "https://synthesia.io", "use_case": "Professional AI videos"},
            {"name": "D-ID", "url": "https://d-id.com", "use_case": "Talking head from photo"},
        ],
        "editing": [
            {"name": "Descript", "url": "https://descript.com", "use_case": "Edit video like text"},
            {"name": "Canva", "url": "https://canva.com", "use_case": "Quick thumbnails/graphics"},
        ]
    }


if __name__ == "__main__":
    test_prospect = {
        "name": "John Smith",
        "company": "Tampa Bay HVAC",
        "industry": "HVAC",
        "email": "john@tampahvac.com"
    }
    
    print("Generating video script...")
    result = generate_video_script(test_prospect, "intro")
    
    if 'script' in result:
        print("\n--- VIDEO SCRIPT ---")
        print(result['script'])
    
    print("\n--- VIDEO PLATFORMS ---")
    print(json.dumps(get_video_platforms(), indent=2))
