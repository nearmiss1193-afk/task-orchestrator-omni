"""Import +1 863-946-5043 from Twilio to Vapi and attach Sarah"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
TARGET_NUMBER = "+18639465043"  # +1 863-946-5043

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

print("=== IMPORTING NUMBER FROM TWILIO TO VAPI ===")
print(f"Target: {TARGET_NUMBER}")
print(f"Sarah ID: {SARAH_ID}")

# Import from Twilio
payload = {
    "provider": "twilio",
    "number": TARGET_NUMBER,
    "twilioAccountSid": TWILIO_SID,
    "twilioAuthToken": TWILIO_TOKEN,
    "assistantId": SARAH_ID,
    "smsEnabled": True,
    "name": "Sarah AI Line"
}

print("\nSending import request...")
r = requests.post(
    "https://api.vapi.ai/phone-number",
    headers=headers,
    json=payload
)

print(f"Status: {r.status_code}")
if r.ok:
    result = r.json()
    print("SUCCESS!")
    print(f"Phone ID: {result.get('id')}")
    print(f"Number: {result.get('number')}")
    print(f"Assistant: {result.get('assistantId')}")
    print(f"SMS Enabled: {result.get('smsEnabled')}")
else:
    print(f"ERROR: {r.text}")
    if "already exists" in r.text.lower():
        print("\nNumber may already exist - checking existing numbers...")
    elif "not found" in r.text.lower():
        print("\nNumber not found in your Twilio account. Verify it exists.")
    elif "10dlc" in r.text.lower() or "a2p" in r.text.lower():
        print("\nNumber needs 10DLC/A2P registration for SMS in Twilio first.")
