"""
MODAL WEBHOOK SERVER - FastAPI deployed to Modal cloud
24/7 webhook endpoint for GHL inbound SMS
"""
import modal
from datetime import datetime

app = modal.App("webhook-server")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi")

# Config
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
BOOKING_LINK = "https://link.aiserviceco.com/discovery"

SARAH_PROMPT = """You are Sarah, the inbound contact handler for AI Service Co.
Handle SMS. Qualify leads, book appointments. Be warm and professional.
Booking link: {booking_link} | Pricing: $297/$497/$997
If STOP, opt out. Keep responses under 160 chars."""


@app.function(image=image, timeout=60)
@modal.web_endpoint(method="GET")
def health():
    """Health check"""
    return {"status": "ok", "service": "webhook-server", "agent": "sarah", "timestamp": datetime.utcnow().isoformat()}


@app.function(image=image, timeout=60)
@modal.web_endpoint(method="POST")
def webhook(data: dict):
    """Main GHL webhook endpoint"""
    import requests
    
    phone = data.get("phone", "") or data.get("contact_phone", "") or data.get("from", "")
    message = data.get("message", "") or data.get("body", "") or data.get("text", "")
    
    print(f"[INBOUND] {phone}: {message[:50]}...")
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    # Check opt-out
    if any(word in message.upper() for word in ["STOP", "UNSUBSCRIBE", "CANCEL"]):
        requests.post(f"{SUPABASE_URL}/rest/v1/event_log", headers=headers, json={
            "event_type": "opt_out", "phone": phone, "success": True
        })
        return {"status": "ok", "action": "opt_out"}
    
    # Get memory
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/memories?phone=eq.{phone}", headers=headers)
        memories = r.json() if r.status_code == 200 else []
        memory_context = "\n".join([f"- {m['key']}: {m['value']}" for m in memories]) or "New contact."
    except:
        memory_context = "New contact."
    
    # Generate Sarah response
    prompt = f"""{SARAH_PROMPT.format(booking_link=BOOKING_LINK)}
    
Memory: {memory_context}
Message: "{message}"

Respond as Sarah. Short, booking-focused."""

    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        response_text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()[:160]
    except:
        response_text = f"Hi! Book a free call: {BOOKING_LINK} -Sarah"
    
    # Log interaction
    requests.post(f"{SUPABASE_URL}/rest/v1/interactions", headers=headers, json={
        "phone": phone, "direction": "inbound", "channel": "sms",
        "message": message, "response": response_text, "agent": "sarah"
    })
    
    # Send response via GHL
    requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": response_text}, timeout=15)
    
    return {"status": "ok", "action": "responded", "response": response_text}


@app.function(image=image, timeout=60)
@modal.web_endpoint(method="POST")
def inbound(data: dict):
    """Alias for /webhook"""
    return webhook.local(data)


@app.function(image=image, timeout=60)
@modal.web_endpoint(method="POST")
def sms(data: dict):
    """SMS-specific endpoint"""
    return webhook.local(data)


@app.local_entrypoint()
def main():
    print("=" * 50)
    print("WEBHOOK SERVER DEPLOYED TO MODAL")
    print("=" * 50)
    print("Endpoints:")
    print("  GET  nearmiss1193-afk--webhook-server-health.modal.run")
    print("  POST nearmiss1193-afk--webhook-server-webhook.modal.run")
    print("  POST nearmiss1193-afk--webhook-server-inbound.modal.run")
    print("  POST nearmiss1193-afk--webhook-server-sms.modal.run")
    print("=" * 50)
