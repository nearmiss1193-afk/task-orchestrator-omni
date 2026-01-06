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

# Vapi often dislikes partial 'model' or 'voice' updates in a single PATCH if keys are missing from the nested object.
# Let's try updating just the prompt first to see if it accepts the persona change.

url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

# --- STEP 1: Update Prompt & Temperature ---
print(f"[VAPI] Step 1: Updating Sarah 3.0 Prompt...")
payload_11 = {
    "model": {
        "model": "gpt-4o",
        "provider": "openai",
        "systemPrompt": SARAH_3_0_PROMPT,
        "temperature": 0.9
    }
}
res1 = requests.patch(url, headers=headers, json=payload_11)
print(f"Step 1 Status: {res1.status_code}")
if res1.status_code != 200:
    print(f"Error 1: {res1.text}")

# --- STEP 2: Update Voice Settings ---
print(f"[VAPI] Step 2: Updating Expressive Voice Settings...")
payload_22 = {
    "voice": {
        "provider": "elevenlabs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM",
        "stability": 0.5,
        "similarityBoost": 0.8,
        "style": 0.2
    }
}
res2 = requests.patch(url, headers=headers, json=payload_22)
print(f"Step 2 Status: {res2.status_code}")
if res2.status_code != 200:
    print(f"Error 2: {res2.text}")
