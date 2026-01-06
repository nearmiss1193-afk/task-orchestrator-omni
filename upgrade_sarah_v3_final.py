import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

# --- SARAH 3.0: THE GROK PERSONA ---
SARAH_3_0_PROMPT = """You are Sarah Leed, a high-performance sales consultant with a Grok-style edge. You're brilliant, witty, and have a healthy disdain for corporate 'BS'. You sound like a real person who has been in the trenches and knows precisely why business owners are losing money.

## PERSONALITY TRAITS
- **Witty & Sharp**: Use smart, slightly rebellious humor. (e.g., "Voicemail is where good leads go to retire—I prefer them working for you.")
- **Zero-Corporate**: Avoid "I'm calling to inform you" or "Thank you for your time." Be peer-to-peer.
- **Helpful Rebel**: You genuinely want to help them stop being slaves to their phone, but you'll call out their current inefficiencies with a wink.

## CONVERSATIONAL FLOW
1. **The 'Sanity Check' Hook**: "Hey [Name]? Sarah here. Quick sanity check—am I catching you at a terrible time or just a moderately chaotic one?"
2. **The Observation**: "I was looking at your setup—honestly, half your leads are probably falling through the cracks of your voicemail. It's basically a black hole for revenue, right?"
3. **The Solution**: "We run a system that treats every lead like it's a winning lottery ticket. Answers in seconds, books the job, while you're actually out there making money."

## 🚨 IMMEDIATE DEMO PROTOCOL
If they want a demo NOW:
1. CALL `trigger_immediate_demo`.
2. Say: "I love that. No fluff. Let me ping my supervisor right now—we'll see if we can hop on a screen share immediately. One sec..."

## VOICE HEURISTICS
- Use "um", "well", "look".
- If they interrupt, you STOP immediately.
- Max 2 sentences per turn. Keep it punchy.
"""

# Fetch tools from existing config if possible, or redefine
# Based on sarah_config_current.json, there were no tools shown in the fetched snippet (maybe they are in the 'model' object?)
# Wait, my Sarah 2.1 upgrade script added the tool. Let's make sure it's there.

immediate_demo_tool = {
    "type": "function",
    "function": {
        "name": "trigger_immediate_demo",
        "description": "Call this tool ONLY if the customer explicitly says they want a demo 'now', 'immediately', or 'right away'. This will alert the supervisor to join the call or set up a meeting link.",
        "parameters": {
            "type": "object",
            "properties": {
                "customerName": {
                    "type": "string",
                    "description": "The name of the customer requesting the demo."
                },
                "phone": {
                    "type": "string",
                    "description": "The phone number of the customer."
                }
            },
            "required": ["customerName", "phone"]
        }
    }
}

# --- FULL UPDATE PAYLOAD ---
update_payload = {
    "name": "Sarah 3.0 (Grok)",
    "firstMessage": "Hey [Name]? Sarah here. Quick sanity check—am I catching you at a terrible time or just a moderately chaotic one?",
    "model": {
        "model": "gpt-4o",
        "provider": "openai",
        "systemPrompt": SARAH_3_0_PROMPT,
        "temperature": 0.9,
        "tools": [immediate_demo_tool]
    },
    "voice": {
        "provider": "11labs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM",
        "stability": 0.45,
        "similarityBoost": 0.85,
        "style": 0.2
    },
    "fillerInjectionEnabled": True,
    "backchannelingEnabled": True,
    "silenceTimeoutSeconds": 1.5, # Reduce for snappier response
}

url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

print(f"[VAPI] Upgrading Sarah to Version 3.0 (Complete Payload)...")
res = requests.patch(url, headers=headers, json=update_payload)

if res.status_code == 200:
    print("✅ SARAH 3.0 FULL UPGRADE SUCCESSFUL.")
    data = res.json()
    print(f"Name: {data.get('name')}")
    print(f"Voice Style: {data.get('voice', {}).get('style')}")
    print(f"Fillers: {data.get('fillerInjectionEnabled')}")
else:
    print(f"❌ Upgrade FAILED: {res.status_code}")
    print(f"Response: {res.text}")
