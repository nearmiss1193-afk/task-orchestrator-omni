import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}"
}

print(f"[VAPI] Fetching current config for Assistant ID: {ASSISTANT_ID}...")
res = requests.get(url, headers=headers)

if res.status_code == 200:
    print("✅ Configuration Fetched.")
    with open("sarah_config_current.json", "w") as f:
        json.dump(res.json(), f, indent=2)
    print("Saved to sarah_config_current.json")
else:
    print(f"❌ Failed: {res.status_code}")
    print(res.text)
