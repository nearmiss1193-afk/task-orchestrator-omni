"""
Test Vapi Outbound Call - Debug Version
"""
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("VAPI_PRIVATE_KEY")
phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")

print(f"Key: {key[:15]}...")
print(f"Phone Number ID: {phone_number_id}")

# First, let's get the CORRECT assistant ID from the account
print("\n=== Getting Correct IDs ===")
r = requests.get("https://api.vapi.ai/assistant", headers={"Authorization": f"Bearer {key}"})
if r.status_code == 200:
    assistants = r.json()
    print(f"Found {len(assistants)} assistants:")
    for a in assistants:
        print(f"  {a.get('id')[:20]}... - {a.get('name')}")
    
    # Use first assistant
    if assistants:
        assistant_id = assistants[0]["id"]
        print(f"\nUsing assistant: {assistant_id}")

# Get phone numbers
r2 = requests.get("https://api.vapi.ai/phone-number", headers={"Authorization": f"Bearer {key}"})
if r2.status_code == 200:
    phones = r2.json()
    print(f"\nFound {len(phones)} phone numbers:")
    for p in phones:
        print(f"  {p.get('id')} - {p.get('number')}")
    
    if phones:
        phone_number_id = phones[0]["id"]
        print(f"\nUsing phone: {phone_number_id}")

# Now make the call with correct IDs
print("\n=== Attempting Outbound Call ===")
payload = {
    "type": "outboundPhoneCall",
    "phoneNumberId": phone_number_id,
    "assistantId": assistant_id,
    "customer": {
        "number": "+13529368152"
    }
}

print(f"Payload: {json.dumps(payload, indent=2)}")

r3 = requests.post(
    "https://api.vapi.ai/call",
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    },
    json=payload
)

print(f"\nStatus: {r3.status_code}")
print(f"Response: {r3.text}")
