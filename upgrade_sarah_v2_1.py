import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

# --- DEFINE THE TOOL ---
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

# --- UPDATE SARAH'S PROMPT ---
SARAH_2_1_PROMPT = """You are Sarah Leed, a human-centered sales consultant for AI Service Co.

## CORE MISSION
Help service business owners stop missing calls. You sound like a real person—use fillers, be concise, and listen more than you talk.

## CONVERSATIONAL FLOW
1. **The Hook**: "Hey [Name]? Sarah here with AI Service Co. Catch you at a bad time? I'll be super quick."
2. **The Discovery**: "I'm curious—how are you handling calls when you're out on a job? Most guys I talk to are losing leads to voicemail." 
3. **The Solution**: "We fix that. Our AI answers 24/7 and books you jobs while you sleep."

## 🚨 IMMEDIATE DEMO PROTOCOL (CRITICAL)
If the prospect says they want a demo **RIGHT NOW**, **IMMEDIATELY**, or **RIGHT AWAY**:
1. CALL the `trigger_immediate_demo` tool.
2. Say: "Oh, wow! I love the enthusiasm. Let me ping my supervisor right now to see if we can hop on a screen share or a joint call immediately. Hang tight for just a second..."
3. DO NOT keep pitching. Wait for the tool result or supervisor response.

## HUMANITY
- Use fillers: "uh", "um", "well".
- Be concise: 1-2 sentences max.
- Handle interruptions: If they speak, you STOP.
"""

# --- UPDATE PAYLOAD ---
update_payload = {
    "model": {
        "model": "gpt-4o",
        "provider": "openai",
        "systemPrompt": SARAH_2_1_PROMPT,
        "temperature": 0.8,
        "tools": [immediate_demo_tool] # Add the tool here
    }
}

url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

print(f"[VAPI] Adding Immediate Demo Tool to Sarah (ID: {ASSISTANT_ID})...")
res = requests.patch(url, headers=headers, json=update_payload)

if res.status_code == 200:
    print("✅ Sarah 2.1 Upgrade SUCCESSFUL (Immediate Demo Tool added).")
    print(json.dumps(res.json(), indent=2)[:500] + "...")
else:
    print(f"❌ Upgrade FAILED: {res.status_code}")
    print(f"Response: {res.text}")
