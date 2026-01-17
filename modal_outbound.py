"""
SOVEREIGN ORCHESTRATOR - OUTBOUND HANDLER (Christina)
Single-function app for reliable deployment
"""
import modal

app = modal.App("orch-outbound")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi")

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
BOOKING_LINK = "https://link.aiserviceco.com/discovery"

@app.function(image=image, timeout=60)
@modal.web_endpoint(method="POST")
def handle_outbound(data: dict):
    """Handle outbound campaign task - Routes to Christina"""
    import requests
    
    phone = data.get("phone", "")
    company = data.get("company", "your business")
    touch = data.get("touch", 1)
    
    print(f"[OUTBOUND] Touch {touch} to {phone}")
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    # Christina's touch messages
    touch_templates = {
        1: f"Hi! I'm Christina from AI Service Co. I just reviewed {company}'s marketing - there are quick wins you're missing. Book a free call: {BOOKING_LINK}",
        2: f"Quick follow-up on {company} - I found 3 things that could help you get more leads this month. Got 15 min? {BOOKING_LINK}",
        3: f"Last chance - I'm moving on tomorrow. If you want the free strategy session for {company}, grab it now: {BOOKING_LINK}"
    }
    
    response_text = touch_templates.get(touch, touch_templates[1])
    
    # Log interaction
    requests.post(f"{SUPABASE_URL}/rest/v1/interactions", headers=headers, json={
        "phone": phone, "direction": "outbound", "channel": "sms",
        "message": response_text, "agent": "christina", "touch": touch
    })
    
    # Send via GHL
    requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": response_text}, timeout=15)
    
    return {"agent": "christina", "touch": touch, "sent": True}
