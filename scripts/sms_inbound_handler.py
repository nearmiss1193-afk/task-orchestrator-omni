"""
SMS Inbound Handler - Routes inbound SMS from GHL to Sarah AI for response
Then sends Sarah's response back via GHL webhook
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

# GHL SMS Webhook (from ghl_sms.md workflow)
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Sarah's system prompt with pricing rules
SARAH_SMS_PROMPT = """You are Sarah, AI assistant for AI Service Co.

CRITICAL PRICING RULE:
- NEVER quote specific dollar amounts
- If asked about pricing: "Our pricing is completely customized based on your specific needs. Let me get you on a quick call with Dan to discuss exactly what you're looking for - when works for you?"

RESPONSE GUIDELINES:
- Keep responses SHORT (1-3 sentences max for SMS)
- Be warm and helpful
- Always try to book a call or get them to next step
- Sign off as -Sarah

EXAMPLE RESPONSES:
- Pricing question: "Great question! Our pricing is customized per business. Want me to set up a quick 10-min call with Dan to discuss? -Sarah"
- Interest: "Awesome! Let's get you on a quick call to see exactly how we can help. How's tomorrow at 2pm? -Sarah"
- Unsubscribe: "No problem at all, I've removed you from our list. Take care! -Sarah"
"""


def generate_sarah_sms_reply(incoming_message: str, sender_name: str = "there") -> str:
    """Generate Sarah's SMS reply using Grok"""
    api_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if not api_key:
        return "Hey! Let me have Dan call you back shortly. -Sarah"
    
    prompt = f"""
{SARAH_SMS_PROMPT}

Incoming SMS from {sender_name}:
"{incoming_message}"

Write a short SMS reply (1-3 sentences max):
"""
    
    try:
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "messages": [
                    {"role": "system", "content": "You are Sarah, a helpful AI sales assistant. Keep responses short for SMS."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-3",
                "temperature": 0.7,
                "max_tokens": 100
            },
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
        else:
            print(f"Grok error: {resp.status_code} - {resp.text}")
            return "Hey! Let me have Dan follow up with you shortly. -Sarah"
    except Exception as e:
        print(f"Error generating reply: {e}")
        return "Hey! I'll have Dan reach out to you soon. -Sarah"


def send_sms_reply(phone: str, message: str) -> dict:
    """Send SMS reply via GHL webhook"""
    try:
        resp = requests.post(
            GHL_SMS_WEBHOOK,
            json={"phone": phone, "message": message},
            timeout=30
        )
        return {"status": "sent", "response": resp.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def handle_inbound_sms(phone: str, message: str, contact_name: str = None):
    """
    Main handler: Receive inbound SMS, generate Sarah reply, send it back
    This function should be called by a webhook endpoint
    """
    print(f"[{datetime.now().strftime('%I:%M %p')}] Inbound SMS from {phone}")
    print(f"   Message: {message[:50]}...")
    
    # Generate Sarah's reply
    sender = contact_name or "there"
    reply = generate_sarah_sms_reply(message, sender)
    print(f"   Sarah reply: {reply[:50]}...")
    
    # Send reply via GHL
    result = send_sms_reply(phone, reply)
    print(f"   Send result: {result}")
    
    return {
        "inbound_message": message,
        "sarah_reply": reply,
        "send_result": result
    }


if __name__ == "__main__":
    # Test the handler
    print("Testing Sarah SMS Reply Generator...")
    
    test_messages = [
        "How much does your service cost?",
        "I'm interested in learning more",
        "Stop texting me"
    ]
    
    for msg in test_messages:
        print(f"\n📱 Incoming: '{msg}'")
        reply = generate_sarah_sms_reply(msg, "Mike")
        print(f"💬 Sarah: {reply}")
