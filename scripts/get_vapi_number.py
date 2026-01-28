import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.environ.get("VAPI_PRIVATE_KEY")
PHONE_ID = os.environ.get("VAPI_PHONE_NUMBER_ID")

headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

try:
    resp = requests.get(f"https://api.vapi.ai/phone-number/{PHONE_ID}", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"📞 Vapi Phone Number: {data.get('number')}")
    else:
        print(f"❌ Error: {resp.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
