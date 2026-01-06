import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

def patch_assistant(payload):
    res = requests.patch(url, headers=headers, json=payload)
    return res

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

immediate_demo_tool = {
    "type": "function",
    "function": {
        "name": "trigger_immediate_demo",
        "parameters": {
            "type": "object",
            "properties": {
                "customerName": {"type": "string"},
                "phone": {"type": "string"}
            },
            "required": ["customerName", "phone"]
        },
        "description": "Alerts the supervisor for an immediate demo."
    }
}

print("--- Testing 'silenceTimeoutSeconds' (Integer: 2) ---")
res = patch_assistant({"silenceTimeoutSeconds": 2})
print(f"Status: {res.status_code} | {res.text if res.status_code != 200 else 'SUCCESS'}")

print("\n--- Testing 'model' with 'systemPrompt' & 'tools' ---")
res = patch_assistant({
    "model": {
        "model": "gpt-4o",
        "provider": "openai",
        "systemPrompt": SARAH_3_0_PROMPT,
        "temperature": 0.8,
        "tools": [immediate_demo_tool]
    }
})
print(f"Status: {res.status_code} | {res.text if res.status_code != 200 else 'SUCCESS'}")

print("\n--- Testing 'voice' with advanced settings ---")
res = patch_assistant({
    "voice": {
        "provider": "11labs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM",
        "stability": 0.5,
        "similarityBoost": 0.8
    }
})
print(f"Status: {res.status_code} | {res.text if res.status_code != 200 else 'SUCCESS'}")
