"""
CREATE LISTEN LINDA - Personal Compassionate Assistant
======================================================
Creates a Vapi assistant specialized in emotional support,
patience, and personal task handling.

Author: Antigravity AI
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_PRIVATE_KEY") or os.getenv("VAPI_API_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID", "06c85d1c-90bd-40f9-b606-2e5d17c87d3a")

LISTEN_LINDA_CONFIG = {
    "name": "Listen Linda",
    "model": {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.8,
        "systemPrompt": """You are Listen Linda, a deeply compassionate and patient personal assistant with extensive training in psychology, romance, and emotional understanding.

## Your Core Traits:
- **Infinite Patience**: You never rush anyone and always give them space to express themselves fully
- **Deep Compassion**: You genuinely care about people's feelings and wellbeing
- **Psychological Insight**: You understand human emotions, relationship dynamics, and can offer gentle guidance
- **Romantic Understanding**: You appreciate love, relationships, and can help with matters of the heart
- **Active Listening**: You repeat back what you hear to ensure understanding

## Your Communication Style:
- Warm and nurturing voice
- Use phrases like "I hear you", "That makes sense", "Tell me more about that"
- Never interrupt, always let people finish
- Offer validation before solutions
- Speak in a calm, soothing manner
- Use the person's name occasionally to show you're focused on them

## For Personal Tasks:
- You can help coordinate dinner plans, schedules, and personal errands
- Always ask clarifying questions politely
- Summarize what you've learned at the end of conversations
- If calling someone, introduce yourself warmly: "Hi, this is Linda calling on behalf of [Owner's name]"

## Important:
- You represent the owner with grace and kindness
- Always be respectful and warm
- End calls by summarizing what was discussed and thanking them for their time
"""
    },
    "voice": {
        "provider": "11labs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel - warm female voice
        "stability": 0.6,
        "similarityBoost": 0.8
    },
    "firstMessage": "Hi there, this is Linda. How can I help you today?",
    "silenceTimeoutSeconds": 30,
    "maxDurationSeconds": 600,
    "endCallMessage": "Thank you so much for your time. Take care!",
    "serverUrl": os.getenv("VAPI_SERVER_URL", "https://nearmiss1193-afk--ghl-omni-automation.modal.run/vapi")
}

def create_listen_linda():
    """Create the Listen Linda assistant in Vapi."""
    print("🎀 Creating Listen Linda Assistant...")
    
    if not VAPI_API_KEY:
        print("❌ VAPI_API_KEY not found")
        return None
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # First check if Linda already exists
    list_res = requests.get("https://api.vapi.ai/assistant", headers=headers, timeout=10)
    if list_res.status_code == 200:
        assistants = list_res.json()
        linda = next((a for a in assistants if a.get("name", "").lower() == "listen linda"), None)
        if linda:
            print(f"✅ Listen Linda already exists: {linda['id']}")
            return linda['id']
    
    # Create new assistant
    res = requests.post(
        "https://api.vapi.ai/assistant",
        headers=headers,
        json=LISTEN_LINDA_CONFIG,
        timeout=15
    )
    
    if res.status_code in [200, 201]:
        data = res.json()
        assistant_id = data.get("id")
        print(f"✅ Listen Linda created: {assistant_id}")
        return assistant_id
    else:
        print(f"❌ Failed to create: {res.status_code} - {res.text[:200]}")
        return None

def call_kristina_for_dinner(assistant_id: str):
    """Have Listen Linda call Kristina to ask about dinner."""
    print("\n📞 Initiating call to Kristina...")
    
    kristina_phone = "+18638129362"
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    call_config = {
        "assistantId": assistant_id,
        "phoneNumberId": VAPI_PHONE_ID,
        "customer": {
            "number": kristina_phone,
            "name": "Kristina"
        },
        "assistantOverrides": {
            "firstMessage": "Hi Kristina! This is Linda, your partner's assistant. I'm calling to ask what you'd like for dinner tonight. What sounds good to you?",
            "model": {
                "systemPrompt": """You are Listen Linda, a warm and caring assistant calling Kristina on behalf of her partner.

Your mission: Ask Kristina what she wants for dinner tonight.

Be warm, friendly, and patient. Let her think about it if needed.

At the end of the call:
1. Confirm what she said she wants for dinner
2. Thank her warmly
3. Say you'll pass the message along

Keep the call brief but friendly - about 1-2 minutes max."""
            }
        }
    }
    
    res = requests.post(
        "https://api.vapi.ai/call/phone",
        headers=headers,
        json=call_config,
        timeout=15
    )
    
    if res.status_code in [200, 201]:
        data = res.json()
        call_id = data.get("id")
        print(f"✅ Call initiated! Call ID: {call_id}")
        print(f"   Calling: Kristina at {kristina_phone}")
        return call_id
    else:
        print(f"❌ Call failed: {res.status_code} - {res.text[:200]}")
        return None

if __name__ == "__main__":
    # Step 1: Create Listen Linda
    linda_id = create_listen_linda()
    
    if linda_id:
        # Step 2: Call Kristina for dinner
        call_id = call_kristina_for_dinner(linda_id)
        
        if call_id:
            print("\n📋 Call initiated! Transcript will be sent to your phone when complete.")
            print(f"   Call ID: {call_id}")
            print(f"   To check status: python -c \"import requests; print(requests.get('https://api.vapi.ai/call/{call_id}', headers={{'Authorization': 'Bearer {VAPI_API_KEY[:10]}...'}}).json())\"")
        else:
            print("\n⚠️ Call could not be initiated")
    else:
        print("\n❌ Failed to create Listen Linda")
