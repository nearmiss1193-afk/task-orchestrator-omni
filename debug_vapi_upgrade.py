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

def patch_key(key, value):
    print(f"--- Attempting to update '{key}' ---")
    payload = {key: value}
    res = requests.patch(url, headers=headers, json=payload)
    print(f"Status: {res.status_code}")
    if res.status_code != 200:
        print(f"Response: {res.text}")
        return False
    print(f"SUCCESS: {key} updated.")
    return True

# 1. Name
if not patch_key("name", "Sarah 3.0 (Grok)"): exit()

# 2. firstMessage
if not patch_key("firstMessage", "Hey [Name]? Sarah here. Quick sanity check—am I catching you at a terrible time or just a moderately chaotic one?"): exit()

# 3. Model (Basic)
model_payload = {
    "model": "gpt-4o",
    "provider": "openai",
    "temperature": 0.8
}
if not patch_key("model", model_payload): exit()

# 4. Voice (Basic)
voice_payload = {
    "provider": "11labs",
    "voiceId": "21m00Tcm4TlvDq8ikWAM"
}
if not patch_key("voice", voice_payload): exit()

print("\n🎉 ALL BASIC UPDATES SUCCESSFUL.")
