"""Enable transcripts for Sarah"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "recordingEnabled": True,
    "transcriber": {
        "provider": "deepgram",
        "model": "nova-2",
        "language": "en"
    }
}

print("Enabling transcripts...")
response = requests.patch(url, headers=headers, json=payload, timeout=30)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Transcripts enabled!")
