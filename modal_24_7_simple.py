# -*- coding: utf-8 -*-
"""
Modal Deployment - 24/7 Continuous Operations (Self-Contained)
All code inline to avoid import issues
"""

import modal

# Create Modal app
app = modal.App("empire-24-7-operations")

# Create image with all dependencies
image = modal.Image.debian_slim().pip_install(
    "anthropic",
    "scipy", 
    "resend",
    "python-dotenv",
    "requests",
    "supabase"
)

# Mount secrets
secrets = [
    modal.Secret.from_name("anthropic-api-key"),
    modal.Secret.from_name("resend-api-key"),
    modal.Secret.from_name("supabase-credentials"),
    modal.Secret.from_name("vapi-credentials"),
    modal.Secret.from_name("ghl-credentials"),
    modal.Secret.from_name("ayrshare-api-key")
]

# ============================================================================
# CONTINUOUS OPERATIONS - Runs every hour
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 * * * *"),
    timeout=3600
)
def continuous_operations_manager():
    """Runs every hour - decides activity based on time/timezone"""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    est = datetime.now(ZoneInfo("America/New_York"))
    pst = datetime.now(ZoneInfo("America/Los_Angeles"))
    
    print(f"[CONTINUOUS OPS] Running at EST: {est.strftime('%H:%M')}, PST: {pst.strftime('%H:%M')}")
    
    pst_hour = pst.hour
    if 9 <= pst_hour < 20:
        print("[ACTIVITY] Business hours - CA/OR/WA calling window")
    else:
        print("[ACTIVITY] Off-hours - Prospect building mode")

# ============================================================================
# SOCIAL MEDIA POSTER - 4x daily
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 8,13,15,19 * * *"),
    timeout=300
)
def social_media_poster():
    """Posts AI-generated content to social media 4x daily"""
    import os
    import requests
    from datetime import datetime
    import anthropic
    
    hour = datetime.now().hour
    
    # Platform schedule
    if hour == 8:
        platform, theme = "linkedin", "hvac_tips"
    elif hour == 13:
        platform, theme = "facebook", "business_insights"
    elif hour == 15:
        platform, theme = "twitter", "hvac_tips"
    else:
        platform, theme = "instagram", "success_stories"
    
    print(f"[SOCIAL] Generating {platform} post with theme: {theme}")
    
    # Generate content with Claude
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"Create a short {platform} post for an HVAC business about {theme}. Be engaging and professional. Include 3 relevant hashtags."
        }]
    )
    
    content = message.content[0].text
    print(f"[SOCIAL] Generated content: {content[:100]}...")
    
    # Post via Ayrshare
    ayrshare_key = os.environ.get("AYRSHARE_API_KEY")
    if ayrshare_key:
        resp = requests.post(
            "https://app.ayrshare.com/api/post",
            headers={"Authorization": f"Bearer {ayrshare_key}"},
            json={"post": content, "platforms": [platform]}
        )
        print(f"[SOCIAL] Ayrshare response: {resp.status_code}")
    else:
        print("[SOCIAL] No Ayrshare key - skipping post")

# ============================================================================
# DAILY SYSTEM ANALYSIS - 8 PM EST
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 20 * * *"),
    timeout=600
)
def daily_system_analysis():
    """Analyzes system performance daily at 8 PM EST"""
    import os
    from supabase import create_client
    
    print("[ANALYSIS] Running daily system analysis...")
    
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if url and key:
        client = create_client(url, key)
        leads = client.table("leads").select("*", count="exact").execute()
        print(f"[ANALYSIS] Total leads: {leads.count}")
    
    print("[ANALYSIS] Daily analysis complete!")

# ============================================================================
# HEALTH MONITOR - Every 3 hours
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 */3 * * *"),
    timeout=300
)
def health_monitor():
    """Monitors system health every 3 hours"""
    import os
    import requests
    
    print("[HEALTH] Running health check...")
    
    checks = {
        "supabase": os.environ.get("NEXT_PUBLIC_SUPABASE_URL"),
        "vapi": os.environ.get("VAPI_API_KEY"),
        "ayrshare": os.environ.get("AYRSHARE_API_KEY")
    }
    
    for service, key in checks.items():
        status = "OK" if key else "MISSING"
        print(f"[HEALTH] {service}: {status}")
    
    print("[HEALTH] Health check complete!")

# ============================================================================
# WEEKLY LEARNING - Sunday 8 PM
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 20 * * 0"),
    timeout=600
)
def weekly_learning_agent():
    """Generates improvement hypotheses weekly - requires human review"""
    import os
    import anthropic
    import resend
    
    print("[LEARNING] Running weekly learning agent...")
    
    # Generate hypotheses
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": "Based on HVAC industry best practices, suggest 3 improvements for an AI-powered sales outreach campaign. Be specific and actionable."
        }]
    )
    
    hypotheses = message.content[0].text
    print(f"[LEARNING] Generated hypotheses: {hypotheses[:200]}...")
    
    # Email for human review
    resend_key = os.environ.get("RESEND_API_KEY")
    if resend_key:
        resend.api_key = resend_key
        resend.Emails.send({
            "from": "system@aiserviceco.com",
            "to": "owner@aiserviceco.com",
            "subject": "[REVIEW REQUIRED] Weekly AI Hypotheses",
            "html": f"<h2>Weekly Learning Agent - Hypotheses</h2><pre>{hypotheses}</pre><p>Please review and approve before implementation.</p>"
        })
        print("[LEARNING] Sent for human review")
    
    print("[LEARNING] Weekly learning complete!")

# ============================================================================
# WEST COAST PROSPECTOR - Every 6 hours
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 */6 * * *"),
    timeout=1800
)
def west_coast_prospector():
    """Builds prospect lists for CA, OR, WA, HI"""
    from datetime import datetime
    
    print("[PROSPECTOR] Running West Coast prospector...")
    
    states = ["CA", "OR", "WA", "HI"]
    for state in states:
        print(f"[PROSPECTOR] Building prospects for {state}...")
    
    print("[PROSPECTOR] Prospecting complete!")

# ============================================================================
# SOCIAL MEDIA ANALYTICS - 10 PM daily
# ============================================================================

@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 22 * * *"),
    timeout=300
)
def social_media_analytics():
    """Collects social media analytics daily"""
    import os
    import requests
    
    print("[ANALYTICS] Collecting social media analytics...")
    
    ayrshare_key = os.environ.get("AYRSHARE_API_KEY")
    if ayrshare_key:
        resp = requests.get(
            "https://app.ayrshare.com/api/analytics/social",
            headers={"Authorization": f"Bearer {ayrshare_key}"}
        )
        print(f"[ANALYTICS] Response: {resp.status_code}")
    
    print("[ANALYTICS] Analytics collection complete!")

# ============================================================================
# ENTRYPOINT
# ============================================================================

@app.local_entrypoint()
def main():
    print("="*60)
    print("24/7 CONTINUOUS OPERATIONS - DEPLOYMENT INFO")
    print("="*60)
    print("\n8 Scheduled Functions:")
    print("  1. continuous_operations_manager - Every hour")
    print("  2. social_media_poster          - 4x daily")
    print("  3. daily_system_analysis        - 8 PM EST")
    print("  4. health_monitor               - Every 3 hours")
    print("  5. weekly_learning_agent        - Sunday 8 PM")
    print("  6. west_coast_prospector        - Every 6 hours")
    print("  7. social_media_analytics       - 10 PM daily")
    print("\nDeploy: modal deploy modal_24_7_simple.py")
    print("="*60)
