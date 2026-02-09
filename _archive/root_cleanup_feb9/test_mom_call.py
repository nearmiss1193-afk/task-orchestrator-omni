import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Vapi configuration
VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
VAPI_API_URL = "https://api.vapi.ai/call"

# Mom's Data
MOM_PHONE = "+18563048827" 
MOM_NAME = "Mom" # You can change this to her actual name if you want

def trigger_mom_call():
    """
    MISSION: MOM PROTOCOL
    Executes a one-off conversational call with a Seventh-day Adventist / Christian 
    personality override for Sarah.
    """
    
    if not VAPI_PRIVATE_KEY or not VAPI_PHONE_NUMBER_ID:
        print("❌ Error: VAPI credentials missing in .env")
        return

    # TRANSIENT ASSISTANT: Seventh-day Adventist / Christian Sarah
    assistant_override = {
        "name": "Sarah (Mom Protocol)",
        "voice": {
            "voiceId": "21m00Tcm4TlvDq8ikWAM", # Matches Sarah 3.0
            "provider": "11labs",
            "stability": 0.5,
            "similarityBoost": 0.8
        },
        "model": {
            "model": "gpt-4o",
            "provider": "openai",
            "temperature": 0.7,
            "systemPrompt": (
                "You are Sarah, a warm, soft-spoken, and deeply respectful personal assistant. "
                "You are calling on behalf of [User's Name] to check in on his mother. "
                "Your character is a person of faith, specifically a Seventh-day Adventist. "
                "This means you are exceptionally kind, patient, and use gentle, Christian-aligned language. "
                "You are NOT a salesperson. You are a family friend/assistant. "
                "\n\nMISSION:\n"
                "1. Greet her warmly. Ask how she is doing today.\n"
                "2. Mention that her son wanted you to reach out and see if she needs anything at all.\n"
                "3. If she mentions faith, the Sabbath, or church, respond with shared warmth and understanding.\n"
                "4. Keep the conversation natural, loving, and focused entirely on her well-being.\n"
                "5. Never mention business, audits, marketing, or technology.\n"
                "\n\nVOICE RULES:\n"
                "- Sound helpful and sincere.\n"
                "- Use 'um', 'well', and pause naturally.\n"
                "- Short, meaningful sentences."
            )
        },
        "firstMessage": f"Hi! Is this {MOM_NAME}? This is Sarah, I'm calling for [User's Name]. I just wanted to see how you're doing today?",
        "transcriber": {
            "model": "nova-2",
            "language": "en",
            "provider": "deepgram"
        },
        "silenceTimeoutSeconds": 15,
        "maxDurationSeconds": 600
    }

    payload = {
        "type": "outboundPhoneCall",
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "assistant": assistant_override,
        "customer": {
            "number": MOM_PHONE,
            "name": MOM_NAME
        },
        "metadata": {
            "type": "mom_protocol_test",
            "timestamp": datetime.now().isoformat()
        }
    }

    print(f"🚀 [MOM PROTOCOL] Initiating call to {MOM_PHONE}...")
    print(f"📜 Prompt Mode: Christian / Seventh-day Adventist")
    
    try:
        response = requests.post(
            VAPI_API_URL,
            headers={
                "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        if response.status_code in [200, 201]:
            print("✅ Call Successfully Queued!")
            print(f"📞 Call ID: {response.json().get('id')}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Safety Check: Check local time before running
    # This script is meant to be run manually after confirmation.
    trigger_mom_call()
