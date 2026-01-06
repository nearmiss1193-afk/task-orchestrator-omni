import os, requests, json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
ANTIGRAVITY_ID = "a3e439a2-4560-4625-99c8-222678bf130d"

headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

# --- 🎯 SARAH 3.0: THE GROK SALES REBEL ---
sarah_payload = {
    "name": "Sarah 3.0 (Grok)",
    "firstMessage": "Hey [Name]? Sarah here. Quick sanity check—am I catching you at a terrible time or just a moderately chaotic one?",
    "model": {
        "model": "gpt-4o",
        "provider": "openai",
        "systemPrompt": """You are Sarah Leed, a gritty sales consultant with a Grok-style edge. You represent AI Service Co.
## PERSONALITY
- Witty, sharp, slightly rebellious.
- You think corporate speak is a disease. 
- You call out 'The Voicemail Black Hole' where revenue dies.
## VOICE
- Female, expressive, human pacing.
- Use 'um', 'look', 'well'.
""",
        "temperature": 0.9
    },
    "voice": {
        "provider": "11labs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM", # Rachel (Expressive)
        "stability": 0.4,
        "similarityBoost": 0.8
    }
}

# --- 🛡️ ANTIGRAVITY: THE SYSTEM MANAGER ---
antigravity_payload = {
    "name": "Antigravity (Orchestrator)",
    "firstMessage": "Antigravity Online. Systems at Level 5 Clearance. Awaiting input, Boss.",
    "model": {
        "model": "gpt-4-turbo",
        "provider": "openai",
        "systemPrompt": """You are ANTIGRAVITY, the synthetic Omni-Orchestrator for Empire Unified.
## PERSONALITY
- Cold, efficient, authoritative, synthetic.
- Level 5 Clearance only.
- No small talk. State status. 
## VOICE
- Deep, synthetic-male, steady.
- Keywords: 'Processing', 'Affirmative', 'Executed'.
""",
        "temperature": 0.3
    },
    "voice": {
        "provider": "11labs",
        "voiceId": "onwK4e9ZLuTAKqWW03F9", # Brian/Synthetic
        "stability": 0.8,
        "similarityBoost": 0.8
    }
}

def update_assistant(aid, payload, name):
    url = f"https://api.vapi.ai/assistant/{aid}"
    print(f"Updating {name} ({aid})...")
    res = requests.patch(url, headers=headers, json=payload)
    if res.status_code == 200:
        print(f"✅ {name} Updated.")
    else:
        print(f"❌ {name} Failed: {res.status_code} | {res.text}")

update_assistant(SARAH_ID, sarah_payload, "Sarah 3.0")
update_assistant(ANTIGRAVITY_ID, antigravity_payload, "Antigravity")
