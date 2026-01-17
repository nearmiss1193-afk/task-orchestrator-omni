"""
SOVEREIGN ORCHESTRATOR - Unified ASGI App
All routes bundled into one FastAPI app for reliable Modal deployment.
"""
import modal
from fastapi import FastAPI
from datetime import datetime
import json

image = modal.Image.debian_slim(python_version="3.11").pip_install("fastapi[standard]", "requests")
app = modal.App("empire-api-v1", image=image)

# Config (Constants)
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"
RESEND_API_KEY = "re_6q5Rx16W_NJbL5Mj44uFy6u1e1MFAq8gy"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
BOOKING_LINK = "https://link.aiserviceco.com/discovery"
ESCALATION_PHONE = "+13529368152"

# Agent system prompts
SARAH_PROMPT = """You are Sarah, the inbound contact handler for AI Service Co.
You handle incoming SMS and calls. You qualify leads, answer questions, and book appointments.
Be warm, professional, and helpful. Offer the booking link early: {booking_link}
Pricing: $297 Starter, $497 Lite, $997 Growth (no contracts)
If frustrated or emergency, escalate. If STOP, opt out immediately."""

CHRISTINA_PROMPT = """You are Christina, the outbound sales specialist for AI Service Co.
You drive proactive outbound engagement. You are a confident closer.
Use urgency and value. Handle objections directly.
Booking link: {booking_link} | Pricing: $297 Starter, $497 Lite, $997 Growth
Push for the booking. Be direct but not pushy."""

@app.function()
@modal.asgi_app()
def orchestration_api():
    import requests
    
    api = FastAPI(title="Sovereign Orchestrator", version="2.0")
    
    @api.get("/health")
    def health():
        """Health check endpoint"""
        return {
            "status": "ok",
            "orchestrator": "sovereign",
            "agents": ["sarah", "christina"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.post("/inbound")
    def handle_inbound(data: dict):
        """Handle inbound SMS/call - Routes to Sarah"""
        phone = data.get("phone", "")
        message = data.get("message", "")
        channel = data.get("channel", "sms")
        
        print(f"[INBOUND] {phone}: {message[:50]}...")
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        # Check for opt-out
        if any(word in message.upper() for word in ["STOP", "UNSUBSCRIBE", "CANCEL"]):
            # Log opt-out
            requests.post(f"{SUPABASE_URL}/rest/v1/event_log", headers=headers, json={
                "event_type": "opt_out", "phone": phone, "success": True, "details": {"message": message}
            })
            return {"agent": "sarah", "action": "opt_out", "response": None}
        
        # Get memory for this contact
        memory_resp = requests.get(f"{SUPABASE_URL}/rest/v1/memories?phone=eq.{phone}", headers=headers)
        memories = memory_resp.json() if memory_resp.status_code == 200 else []
        memory_context = "\n".join([f"- {m['key']}: {m['value']}" for m in memories]) or "No previous memory."
        
        # Generate Sarah's response
        prompt = f"""{SARAH_PROMPT.format(booking_link=BOOKING_LINK)}

Customer memory:
{memory_context}

Customer message: "{message}"

Respond as Sarah. Keep it short (under 160 chars for SMS). Be helpful and push for booking if appropriate."""

        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            response_text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"Gemini error: {e}")
            response_text = f"Hi! Thanks for reaching out. Book a free call here: {BOOKING_LINK} -Sarah"
        
        # Log interaction
        requests.post(f"{SUPABASE_URL}/rest/v1/interactions", headers=headers, json={
            "phone": phone, "direction": "inbound", "channel": channel,
            "message": message, "response": response_text, "agent": "sarah"
        })
        
        # Send response via GHL
        requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": response_text}, timeout=15)
        
        return {"agent": "sarah", "response": response_text}
    
    @api.post("/outbound")
    def handle_outbound(data: dict):
        """Handle outbound campaign task - Routes to Christina"""
        phone = data.get("phone", "")
        company = data.get("company", "your business")
        touch = data.get("touch", 1)
        
        print(f"[OUTBOUND] Touch {touch} to {phone}")
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        # Get memory context
        memory_resp = requests.get(f"{SUPABASE_URL}/rest/v1/memories?phone=eq.{phone}", headers=headers)
        memories = memory_resp.json() if memory_resp.status_code == 200 else []
        memory_context = "\n".join([f"- {m['key']}: {m['value']}" for m in memories]) or "New lead."
        
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
    
    return api
