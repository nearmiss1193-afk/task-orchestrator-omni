import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.environ.get("VAPI_PRIVATE_KEY")
PHONE_ID = os.environ.get("VAPI_PHONE_NUMBER_ID")
NEW_URL = "https://nearmiss1193-afk--ghl-omni-automation-universal-web-app.modal.run/office-voice-tool"

if not VAPI_PRIVATE_KEY or not PHONE_ID:
    print("❌ Missing VAPI credentials in .env")
    exit(1)

print(f"📡 Configuring Vapi Phone {PHONE_ID}...")
print(f"🔗 Target: {NEW_URL}")

url = f"https://api.vapi.ai/phone-number/{PHONE_ID}"
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "serverUrl": NEW_URL
}

try:
    resp = requests.patch(url, json=payload, headers=headers)
    if resp.status_code == 200:
        print("✅ Vapi Configuration Updated Successfully!")
        print(resp.json())
    else:
        print(f"❌ Failed to update Vapi: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
