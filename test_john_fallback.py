# test_john_fallback.py - Test John using SARAH'S phone number (verified working)
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
# John's Brain
JOHN_ASSISTANT_ID = "78b4c14a-b44a-4096-82f5-a10106d1bfd2"

# Sarah's Phone (We know this works!)
SARAH_PHONE_ID = "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e"  # +1 863-213-2505

# YOUR NUMBER
YOUR_NUMBER = "+13527585336"

url = "https://api.vapi.ai/call"
headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "assistantId": JOHN_ASSISTANT_ID,
    "phoneNumberId": SARAH_PHONE_ID,
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

print("=" * 50)
print("TEST: JOHN via SARAH'S LINE")
print("=" * 50)
print(f"From: +1 863-213-2505 (Sarah's Line)")
print(f"Using: John's Voice/Brain")
print(f"To: {YOUR_NUMBER}")
print("=" * 50)

res = requests.post(url, headers=headers, json=payload)

if res.status_code == 201:
    print("\n[SUCCESS] Call initiated!")
    print(f"Call ID: {res.json().get('id')}")
    print("\nIf this works, the problem is the NEW number (Carrier issue).")
else:
    print(f"\n[ERROR] {res.status_code}")
    print(res.text)
