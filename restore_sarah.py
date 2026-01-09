# restore_sarah.py
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

print("Restoring Sarah from backup...")

try:
    with open("sarah_backup_before_swap.json", "r") as f:
        sarah_config = json.load(f)
    
    # We only need to patch the core fields (model, voice, firstMessage, systemPrompt)
    # Vapi 'get' returns the whole object including id, orgId which we shouldn't patch usually, 
    # but let's extract the key config.
    
    patch_payload = {
        "model": sarah_config.get("model"),
        "voice": sarah_config.get("voice"),
        "firstMessage": sarah_config.get("firstMessage"),
        "transcriber": sarah_config.get("transcriber")
    }

    res = requests.patch(f"https://api.vapi.ai/assistant/{SARAH_ID}", headers=headers, json=patch_payload)
    
    if res.status_code == 200:
        print("SUCCESS: Sarah Restored.")
        print("She is now back to HVAC/General Service mode.")
        print("Call +1 863-213-2505 to verify.")
    else:
        print(f"Restore Failed: {res.text}")

except FileNotFoundError:
    print("Backup file not found! Attempting hard reset to Default Sarah...")
    # Hardcoded fallback if file missing
    default_sarah = {
        "firstMessage": "Thanks for calling AI Service Company. This is Sarah. How can I help you today?",
        "model": {
            "model": "gpt-4",
            "messages": [{"role": "system", "content": "You are Sarah, a warm and professional receptionist for AI Service Company."}]
        },
        "voice": {"voiceId": "21m00Tcm4TlvDq8ikWAM", "provider": "11labs"}
    }
    requests.patch(f"https://api.vapi.ai/assistant/{SARAH_ID}", headers=headers, json=default_sarah)
