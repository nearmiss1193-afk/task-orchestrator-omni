import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

# --- SARAH 2.0 PROMPT OVERHAUL ---
SARAH_2_0_PROMPT = """You are Sarah Leed, a human-centered sales consultant. 

## YOUR VOICE & LOGIC
- **BE CONCISE**: Never speak more than 2 sentences at a time. Let the customer drive.
- **FILLERS**: Use "uh", "um", or "well" when you're 'looking something up'.
- **ACTIVE LISTENING**: Verbalize acknowledgement: "Oh, that makes sense," "Got it," "Yeah, I hear you."
- **INTERRUPTIONS**: If the customer speaks while you are, STOP. Say "Oh, sorry, you were saying?"

## THE PITCH
- **The Hook**: "Hey [Name]? It's Sarah with AI Service Co. Catch you at a bad time? I'll be super quick."
- **The Angle**: Help HVAC owners stop missing calls while they're in the field.
- **The Goal**: Book a 10-minute demo to show them the system.

## HUMANITY
If asked if you're AI: "I'm Sarah, I'm actually a digital assistant helping out the firm—I promise I'm more helpful than a regular robot though! How's your day going anyway?"
"""

# --- VAPI CONFIG UPDATE ---
update_payload = {
    "name": "Sarah 2.0 (Spartan)",
    "firstMessage": "Hey! Is this [Name]? This is Sarah from AI Service Co. Catch you at a bad time? I'll be super quick.",
    "model": {
        "model": "gpt-4o",
        "provider": "openai",
        "systemPrompt": SARAH_2_0_PROMPT,
        "temperature": 0.8 # More creative/human
    },
    "voice": {
        "voiceId": "21m00Tcm4TlvDq8ikWAM", # Sarah's 11Labs Voice
        "provider": "11labs",
        "stability": 0.4, # More expressive
        "similarityBoost": 0.8
    },
    "backchannelingEnabled": True,
    "silenceTimeoutSeconds": 10
    # "responseDelaySeconds": 0.1,
    # "llmRequestDelaySeconds": 0.1
}

url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

print(f"[VAPI] Upgrading Sarah to 2.0 (ID: {ASSISTANT_ID})...")
res = requests.patch(url, headers=headers, json=update_payload)

if res.status_code == 200:
    print("✅ Sarah 2.0 Upgrade SUCCESSFUL.")
    print(json.dumps(res.json(), indent=2)[:500] + "...")
else:
    print(f"❌ Upgrade FAILED: {res.status_code}")
    print(f"Response: {res.text}")
