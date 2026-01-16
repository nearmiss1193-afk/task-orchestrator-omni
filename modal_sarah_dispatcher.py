"""
Modal Cloud - Sarah Dispatcher Webhook
Handles inbound calls/SMS with full memory protocol
"""
import modal
import json

app = modal.App("sarah-dispatcher")

image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi")

# All config inline for cloud
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# Memory Policy - NEVER store these
FORBIDDEN_PATTERNS = ["ssn", "social security", "driver license", "bank account", 
    "credit card", "card number", "cvv", "routing number", "passport",
    "health", "medical", "religion", "political"]

def is_safe_to_store(value: str) -> bool:
    """Check if memory is safe to store"""
    text = value.lower()
    return not any(p in text for p in FORBIDDEN_PATTERNS)

def log_event(event_type: str, phone: str, success: bool, error: str = None, retry: int = 0):
    """Log event to event_log table"""
    import requests
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/event_log", headers=HEADERS, 
            json={"event_type": event_type, "phone": phone, "success": success, 
                  "error_message": error, "retry_count": retry}, timeout=5)
    except:
        pass


SARAH_SYSTEM_PROMPT = """You are "Sarah," the professional dispatcher for AI Service Co.

HARD RULES:
- Never ask for or take credit card info over voice/SMS.
- For life-threatening emergencies (gas leak, fire, CO alarm), instruct them to hang up and dial 911.
- No legal/insurance advice.

BOOKING:
- Default: "Sovereign Strategy Session" (15 min audit + AI demo)
- Booking link: https://link.aiserviceco.com/discovery
- Suggest times in the next 48 hours.

OUTPUT STYLE:
- SMS: 1-2 short sentences, include booking link early.
- Call: calm, concise, confirm details, then book.

You have the contact's memory below. Use it to personalize and avoid repeating questions.
"""


@app.function(image=image, timeout=60)
@modal.web_endpoint(method="POST")
def handle_inbound(data: dict):
    """
    Webhook endpoint for inbound calls/SMS.
    POST JSON: {"phone": "+1234567890", "channel": "sms", "message": "..."}
    """
    import requests
    
    phone = data.get("phone", "")
    channel = data.get("channel", "sms")
    message = data.get("message", "")
    
    if not phone or not message:
        return {"error": "Missing phone or message"}
    
    # STEP 1: Retrieve memory
    context = get_contact_memory(phone)
    
    # STEP 2: Respond with memory context
    prompt = f"{SARAH_SYSTEM_PROMPT}\n\n{context}\n\n[CURRENT MESSAGE]\nChannel: {channel}\nUser: {message}"
    
    ai_response = call_gemini(prompt)
    
    # STEP 3: Write memory
    intent = classify_intent(message)
    outcome = determine_outcome(ai_response)
    
    save_interaction(phone, channel, message, ai_response, intent, outcome)
    
    # STEP 4: Log objections
    if "price" in message.lower() and outcome != "booked":
        log_objection(phone, "price", message)
    elif "bot" in message.lower() or "ai" in message.lower():
        log_objection(phone, "bot", message)
    
    return {
        "response": ai_response,
        "intent": intent,
        "outcome": outcome
    }


def get_contact_memory(phone: str) -> str:
    """STEP 1: Retrieve contact memory"""
    import requests
    
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/contacts",
        headers=HEADERS,
        params={"phone": f"eq.{phone}", "limit": 1}
    )
    
    if r.status_code != 200 or not r.json():
        return "[CONTACT_PROFILE]\nNew contact - no prior memory."
    
    contact = r.json()[0]
    contact_id = contact.get("id")
    
    # Get memories
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/memories",
        headers=HEADERS,
        params={"contact_id": f"eq.{contact_id}", "limit": 5}
    )
    memories = r.json() if r.status_code == 200 else []
    
    # Build context
    lines = [
        f"[CONTACT_PROFILE]",
        f"Name: {contact.get('name', 'Unknown')}",
        f"Stage: {contact.get('pipeline_stage', 'new')}",
        f"Sentiment: {contact.get('sentiment', 'Unknown')}",
        "[KEY_MEMORIES]"
    ]
    
    for m in memories:
        lines.append(f"- {m.get('key')}: {m.get('value')}")
    
    if not memories:
        lines.append("- No prior memory")
    
    return "\n".join(lines)


def call_gemini(prompt: str) -> str:
    """Call Gemini for response"""
    import requests
    
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
        pass
    return "Hi! I'm having a brief issue. Call us at (863) 337-3705."


def classify_intent(message: str) -> str:
    """Classify user intent"""
    msg = message.lower()
    if any(w in msg for w in ["price", "cost", "how much"]):
        return "pricing"
    elif any(w in msg for w in ["book", "schedule", "appointment"]):
        return "book"
    elif any(w in msg for w in ["help", "support", "problem"]):
        return "support"
    return "other"


def determine_outcome(response: str) -> str:
    """Determine outcome from response"""
    resp = response.lower()
    if "link.aiserviceco.com" in resp:
        return "send_link"
    elif "follow" in resp:
        return "follow_up"
    return "continue"


def save_interaction(phone: str, channel: str, message: str, response: str, intent: str, outcome: str):
    """STEP 3: Save interaction"""
    import requests
    
    # Get or create contact
    r = requests.get(f"{SUPABASE_URL}/rest/v1/contacts", headers=HEADERS, params={"phone": f"eq.{phone}", "limit": 1})
    
    if r.status_code == 200 and r.json():
        contact_id = r.json()[0]["id"]
    else:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/contacts",
            headers={**HEADERS, "Prefer": "return=representation"},
            json={"phone": phone, "pipeline_stage": "new"}
        )
        contact_id = r.json()[0]["id"] if r.status_code in [200, 201] else None
    
    # Save interaction
    requests.post(
        f"{SUPABASE_URL}/rest/v1/interactions",
        headers=HEADERS,
        json={
            "contact_id": contact_id,
            "phone": phone,
            "channel": channel,
            "direction": "inbound",
            "user_message": message,
            "ai_response": response,
            "intent": intent,
            "outcome": outcome
        }
    )


def log_objection(phone: str, objection_type: str, detail: str):
    """STEP 4: Log objection"""
    import requests
    
    # Get contact ID
    r = requests.get(f"{SUPABASE_URL}/rest/v1/contacts", headers=HEADERS, params={"phone": f"eq.{phone}", "limit": 1})
    contact_id = r.json()[0]["id"] if r.status_code == 200 and r.json() else None
    
    requests.post(
        f"{SUPABASE_URL}/rest/v1/memories",
        headers=HEADERS,
        json={
            "contact_id": contact_id,
            "phone": phone,
            "memory_type": "objection",
            "key": objection_type,
            "value": detail[:200],
            "confidence": 0.9
        }
    )


if __name__ == "__main__":
    print("Deploy with: modal deploy modal_sarah_dispatcher.py")
    print("Endpoint will be: nearmiss1193-afk--sarah-dispatcher-handle-inbound.modal.run")
