# call_john_demo.py - Have John call you for a demo (outbound)
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
JOHN_ASSISTANT_ID = "78b4c14a-b44a-4096-82f5-a10106d1bfd2"
ROOFING_PHONE_ID = "40379c46-4b27-45de-8294-4908b694dfc6"  # +1 863-692-8548

# YOUR NUMBER - John will call you
YOUR_NUMBER = "+13529368152"  # User's Verified Cell

url = "https://api.vapi.ai/call"
headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "assistantId": JOHN_ASSISTANT_ID,
    "phoneNumberId": ROOFING_PHONE_ID,
    "customer": {
        "number": YOUR_NUMBER,
        "name": "Boss"
    },
    "assistantOverrides": {
        "variableValues": {
            "customer_name": "Boss",
            "company_name": "Test Roofing Co"
        }
    }
}

print("=" * 40)
print("JOHN OUTBOUND DEMO CALL")
print("=" * 40)
print(f"From: +1 863-692-8548 (John)")
print(f"To: {YOUR_NUMBER}")
print(f"Type: OUTBOUND (Sales pitch)")
print("=" * 40)

res = requests.post(url, headers=headers, json=payload)

if res.status_code == 201:
    data = res.json()
    print("\n[SUCCESS] Call initiated!")
    print(f"Call ID: {data.get('id')}")
    print("\nPick up and test John's persona!")
else:
    print(f"\n[ERROR] {res.status_code}")
    print(res.text)
