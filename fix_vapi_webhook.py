import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('C:/Users/nearm/.gemini/antigravity/scratch/empire-unified/.env')

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a" # Sarah
NEW_SERVER_URL = "https://empire-unified-backup-production.up.railway.app/vapi/webhook"

def update_vapi_webhook():
    print(f"Updating Vapi Assistant {ASSISTANT_ID} to use server: {NEW_SERVER_URL}")
    
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "serverUrl": NEW_SERVER_URL,
        "serverMessages": [
             "conversation-update",
             "end-of-call-report",
             "function-call",
             "hang",
             "model-output",
             "phone-call-control",
             "speech-update",
             "status-update",
             "transcript",
             "tool-calls",
             "transfer-destination-request",
             "user-interrupted",
             "voice-input"
        ] # Ensure we get all events for logging
    }
    
    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        print("✅ Successfully updated Vapi Webhook URL!")
        print(response.json())
    except Exception as e:
        print(f"❌ Failed to update Vapi: {e}")
        if hasattr(e, 'response') and e.response:
             print(e.response.text)

if __name__ == "__main__":
    update_vapi_webhook()
