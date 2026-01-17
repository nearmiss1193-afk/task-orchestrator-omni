"""
LOCAL WEBHOOK SERVER - FastAPI endpoint for GHL webhooks
Runs locally as a fallback or with ngrok for public access
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import json
from datetime import datetime
import uvicorn

app = FastAPI(title="AI Service Co Webhook Server")

# Config
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
BOOKING_LINK = "https://link.aiserviceco.com/discovery"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# Sarah prompt
SARAH_PROMPT = """You are Sarah, the inbound contact handler for AI Service Co.
You handle incoming SMS. Qualify leads, answer questions, book appointments.
Be warm, professional, helpful. Offer booking link early: {booking_link}
Pricing: $297 Starter, $497 Lite, $997 Growth (no contracts)
If STOP, opt out. Keep responses under 160 chars."""


def log(message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {message}")


def process_inbound(data: dict):
    """Process inbound SMS and generate Sarah response"""
    phone = data.get("phone", "") or data.get("contact_phone", "") or data.get("from", "")
    message = data.get("message", "") or data.get("body", "") or data.get("text", "")
    
    log(f"INBOUND from {phone}: {message[:50]}...")
    
    # Check for opt-out
    if any(word in message.upper() for word in ["STOP", "UNSUBSCRIBE", "CANCEL"]):
        requests.post(f"{SUPABASE_URL}/rest/v1/event_log", headers=HEADERS, json={
            "event_type": "opt_out", "phone": phone, "success": True
        })
        log(f"  OPT-OUT: {phone}")
        return {"action": "opt_out", "response": None}
    
    # Get memory
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/memories?phone=eq.{phone}", headers=HEADERS)
        memories = r.json() if r.status_code == 200 else []
        memory_context = "\n".join([f"- {m['key']}: {m['value']}" for m in memories]) or "New contact."
    except:
        memory_context = "New contact."
    
    # Generate response via Gemini
    prompt = f"""{SARAH_PROMPT.format(booking_link=BOOKING_LINK)}

Contact memory:
{memory_context}

Customer message: "{message}"

Respond as Sarah. Short, helpful, push for booking if appropriate."""

    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        response_text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()[:160]
    except Exception as e:
        log(f"  Gemini error: {e}")
        response_text = f"Hi! Thanks for reaching out. Book a free call: {BOOKING_LINK} -Sarah"
    
    # Log interaction
    requests.post(f"{SUPABASE_URL}/rest/v1/interactions", headers=HEADERS, json={
        "phone": phone, "direction": "inbound", "channel": "sms",
        "message": message, "response": response_text, "agent": "sarah"
    })
    
    # Send response via GHL
    try:
        requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": response_text}, timeout=15)
        log(f"  SENT: {response_text[:50]}...")
    except Exception as e:
        log(f"  GHL send error: {e}")
    
    return {"action": "responded", "response": response_text}


@app.get("/")
async def root():
    return {"status": "ok", "service": "AI Service Co Webhook Server", "agent": "sarah"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/webhook")
async def handle_ghl(request: Request):
    """Main GHL webhook endpoint"""
    try:
        data = await request.json()
        log(f"Webhook received: {json.dumps(data)[:100]}")
        result = process_inbound(data)
        return JSONResponse(content={"status": "ok", **result})
    except Exception as e:
        log(f"Webhook error: {e}")
        return JSONResponse(content={"status": "error", "error": str(e)}, status_code=500)


@app.post("/inbound")
async def handle_inbound(request: Request):
    """Alias for /webhook"""
    return await handle_ghl(request)


@app.post("/sms")
async def handle_sms(request: Request):
    """Another alias for SMS-specific webhooks"""
    return await handle_ghl(request)


if __name__ == "__main__":
    print("=" * 50)
    print("AI SERVICE CO WEBHOOK SERVER")
    print("=" * 50)
    print("Endpoints:")
    print("  GET  /        - Status")
    print("  GET  /health  - Health check")
    print("  POST /webhook - GHL webhook")
    print("  POST /inbound - Inbound SMS")
    print("  POST /sms     - SMS handler")
    print("=" * 50)
    print("Starting server on http://localhost:8000")
    print("Use ngrok for public URL: ngrok http 8000")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
