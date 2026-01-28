import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a" # Sarah 3.0
NEW_SERVER_URL = "https://nearmiss1193-afk--nexus-outreach-v1-orchestration-api.modal.run/vapi-webhook"

def update_sarah_server_url():
    print(f"🔧 Updating Sarah's serverUrl to: {NEW_SERVER_URL}")
    
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "serverUrl": NEW_SERVER_URL
    }
    
    try:
        res = requests.patch(url, headers=headers, json=payload)
        if res.status_code == 200:
            print("✅ Sarah's Vapi Configuration Updated.")
        else:
            print(f"❌ Update Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_sarah_server_url()
