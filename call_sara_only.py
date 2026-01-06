import os, requests, json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
USER_PHONE = os.getenv('TEST_PHONE')
PHONE_NUMBER_ID = os.getenv('VAPI_PHONE_NUMBER_ID')
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

print(f"🚀 Triggering Sarah 3.0 (Grok) call to {USER_PHONE}...")

url = 'https://api.vapi.ai/call/phone'
payload = {
    "assistantId": SARAH_ID,
    "phoneNumberId": PHONE_NUMBER_ID,
    "customer": {
        "number": USER_PHONE,
        "name": "Boss"
    }
}
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

try:
    res = requests.post(url, headers=headers, json=payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    if res.status_code == 201 or res.status_code == 200:
        print("✅ Sarah 3.0 Dispatch Successful.")
except Exception as e:
    print(f"❌ Error: {e}")
