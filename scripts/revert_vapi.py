import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.environ.get("VAPI_PRIVATE_KEY")
PHONE_ID = os.environ.get("VAPI_PHONE_NUMBER_ID")

# None translates to null in JSON, which should clear the field
NEW_URL = None 

print(f"🔙 Reverting Vapi Phone {PHONE_ID} to Dashboard Config (Sarah)...")

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
        print("✅ Vapi Configuration Reverted!")
        print(resp.json())
    else:
        print(f"❌ Failed to revert: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
