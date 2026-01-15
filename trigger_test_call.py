import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a" # Sarah 3.0
TEST_PHONE = os.getenv("TEST_PHONE")

def trigger_call():
    print(f"Triggering test call to {TEST_PHONE}...")
    
    resp = requests.post(
        "https://api.vapi.ai/call",
        headers={"Authorization": f"Bearer {VAPI_KEY}", "Content-Type": "application/json"},
        json={
            "type": "outboundPhoneCall",
            "phoneNumberId": VAPI_PHONE_ID,
            "assistantId": SARAH_ID,
            "customer": {"number": TEST_PHONE, "name": "Sovereign Executive"}
        }
    )
    
    if resp.status_code in [200, 201]:
        print("✅ Call Triggered Successfully!")
        print(f"Call ID: {resp.json().get('id')}")
    else:
        print(f"❌ Call Failed: {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    trigger_call()
