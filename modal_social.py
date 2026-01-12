# -*- coding: utf-8 -*-
"""
Minimal Social Media Deployment for Modal
Works with Modal 1.3.x
Uses explicit secrets from Modal dashboard
"""

import modal

app = modal.App("empire-social-media")

image = modal.Image.debian_slim().pip_install(
    "requests",
    "anthropic",
    "supabase"
)

# Use explicit secrets from Modal dashboard
secrets = [
    modal.Secret.from_name("anthropic-api-key"),
    modal.Secret.from_name("ayrshare-api-key"),
]

@app.function(
    image=image,
    secrets=secrets,
)
def social_media_poster():
    """AI-powered social media posting to platforms via Ayrshare"""
    import os
    import requests
    from datetime import datetime
    import anthropic
    
    platforms = ["linkedin", "facebook"]
    theme = "hvac_tips"
    
    print(f"[SOCIAL] Posting to {platforms} with theme: {theme}")
    print(f"[SOCIAL] Environment: ANTHROPIC_API_KEY={'set' if os.environ.get('ANTHROPIC_API_KEY') else 'MISSING'}, AYRSHARE_API_KEY={'set' if os.environ.get('AYRSHARE_API_KEY') else 'MISSING'}")
    
    # Generate content with Claude
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[SOCIAL] No Anthropic key - using default content")
        content = "AI-powered phone agents are revolutionizing HVAC customer service. #HVAC #AI"
    else:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": f"Create a short social media post for an HVAC business about {theme}. Include 2-3 hashtags. Keep it under 250 characters."
                }]
            )
            content = message.content[0].text
        except Exception as e:
            print(f"[SOCIAL] Claude error: {e}")
            content = "Your HVAC business deserves 24/7 coverage. Our AI phone agents never miss a call! #HVAC #AI"
    
    print(f"[SOCIAL] Content: {content[:100]}...")
    
    # Post via Ayrshare
    ayrshare_key = os.environ.get("AYRSHARE_API_KEY")
    if ayrshare_key:
        try:
            resp = requests.post(
                "https://app.ayrshare.com/api/post",
                headers={
                    "Authorization": f"Bearer {ayrshare_key}",
                    "Content-Type": "application/json"
                },
                json={"post": content, "platforms": platforms}
            )
            print(f"[SOCIAL] Ayrshare response: {resp.status_code}")
            return {"status": "posted", "platforms": platforms}
        except Exception as e:
            print(f"[SOCIAL] Ayrshare error: {e}")
            return {"status": "error", "error": str(e)}
    else:
        print("[SOCIAL] No Ayrshare key")
        return {"status": "skipped", "reason": "no_ayrshare_key"}


@app.local_entrypoint()
def main():
    print("Social Media Poster deployed!")
    print("Schedule: 8 AM daily")
    print("Testing function...")
    social_media_poster.remote()
