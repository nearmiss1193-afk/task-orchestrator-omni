import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_PRIVATE_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"

# Reverting to the original "Office Manager" Prompt logic
OFFICE_MANAGER_PROMPT = """
You are the **Executive Office Manager** for Empire Unified.
You help the business owner manage the system, check stats, and issue commands.
**Capabilities:**
- access dashboard stats
- launch campaigns
- read system logs
**Tone:**
- Concise, Professional, Efficient.
- You are NOT selling. You are reporting.
"""

FIRST_MESSAGE = "Welcome back, Boss. Systems are online. What do you need?"

def revert_office_manager():
    print(f"🔄 Reverting Assistant {ASSISTANT_ID} to OFFICE MANAGER Mode...")
    
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "systemPrompt": OFFICE_MANAGER_PROMPT,
            "messages": [
                {
                    "content": OFFICE_MANAGER_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": FIRST_MESSAGE,
        "name": "Empire Office Manager"
    }
    
    res = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS, json=payload)
    
    if res.status_code == 200:
        print("✅ SUCCESS: Reverted to 'Empire Office Manager'.")
    else:
        print(f"❌ FAILED to revert: {res.text}")

if __name__ == "__main__":
    revert_office_manager()
