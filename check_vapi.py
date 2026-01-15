"""Get full Vapi phone config and Sarah assistant details"""
import requests
import json

VAPI_KEY = "c23c884d-0008-4b14-ad5d-530e98d0c9da"
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

# Get all phone numbers with full details
print("=== VAPI PHONE NUMBERS ===")
resp = requests.get(
    "https://api.vapi.ai/phone-number",
    headers={"Authorization": f"Bearer {VAPI_KEY}"}
)
if resp.status_code == 200:
    for n in resp.json():
        print(f"\nNumber: {n.get('number')}")
        print(f"  ID: {n.get('id')}")
        print(f"  Assistant ID: {n.get('assistantId', 'NOT SET')}")
        print(f"  Inbound enabled: {n.get('inboundEnabled', 'NOT SET')}")
        print(f"  Outbound enabled: {n.get('outboundEnabled', 'NOT SET')}")

# Get Sarah assistant details
print("\n=== SARAH ASSISTANT ===")
resp = requests.get(
    f"https://api.vapi.ai/assistant/{SARAH_ID}",
    headers={"Authorization": f"Bearer {VAPI_KEY}"}
)
if resp.status_code == 200:
    sarah = resp.json()
    print(f"Name: {sarah.get('name')}")
    print(f"ID: {sarah.get('id')}")
    print(f"Model: {sarah.get('model', {}).get('provider', 'N/A')}")
    print(f"Voice: {sarah.get('voice', {}).get('provider', 'N/A')}")
else:
    print(f"Error getting Sarah: {resp.status_code}")
