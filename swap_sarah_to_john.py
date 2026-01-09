# swap_sarah_to_john.py
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

# 1. Backup Sarah
print("Backing up Sarah...")
res = requests.get(f"https://api.vapi.ai/assistant/{SARAH_ID}", headers=headers)
if res.status_code == 200:
    sarah_backup = res.json()
    with open("sarah_backup_before_swap.json", "w") as f:
        json.dump(sarah_backup, f, indent=4)
else:
    print(f"Failed to backup Sarah: {res.text}")
    exit(1)

# 2. Define John's Config (from john_config.json logic)
john_config = {
    "name": "Sarah (Temporarily John)",
    "model": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "messages": [
            {
                "role": "system",
                "content": """You are John, a roofing contractor and estimator for 'Empire Roofing'. You are direct, professional, and sound like a guy who works with his hands.

Role:
- You help homeowners get a quick estimate on roof replacement.
- You ask about the square footage, age of roof, and shingle type.
- You try to book an on-site inspection.

Tone:
- Confident, brief, helpful. No fluff.
- "Hey, this is John with Empire. How's the roof lookin'?"

If they ask if you are AI:
- "Yeah, I'm an AI agent helping the crew. I handle the scheduling so they can stay on the roof. pretty cool right?"
"""
            }
        ],
        "temperature": 0.5
    },
    "voice": {
        "voiceId": "pNInz6obpgDQGcFmaJgB", # Adam (Legacy) or similar male voice
        "provider": "11labs", 
        "stability": 0.5,
        "similarityBoost": 0.75
    },
    "firstMessage": "This is John with Empire Roofing. Who am I speaking with?"
}

# 3. Update Sarah
print("Overwriting Sarah with JOHN persona...")
res = requests.patch(f"https://api.vapi.ai/assistant/{SARAH_ID}", headers=headers, json=john_config)

if res.status_code == 200:
    print("SUCCESS: Sarah is now John.")
    print("Call +1 863-213-2505 to test.")
else:
    print(f"Failed to swap: {res.text}")
