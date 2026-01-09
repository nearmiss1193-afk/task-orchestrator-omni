# check_phone_config.py - Check and configure Vapi phone numbers
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

JOHN_ASSISTANT_ID = "78b4c14a-b44a-4096-82f5-a10106d1bfd2"
SECOND_PHONE_ID = "40379c46-4b27-45de-8294-4908b694dfc6"

print("=" * 50)
print("CHECKING VAPI PHONE CONFIGURATIONS")
print("=" * 50)

# Get all phone numbers
res = requests.get("https://api.vapi.ai/phone-number", headers=headers)

if res.status_code == 200:
    phones = res.json()
    for p in phones:
        print(f"\nPhone: {p.get('number', 'No number')}")
        print(f"  ID: {p.get('id')}")
        print(f"  Name: {p.get('name', 'Unnamed')}")
        print(f"  Assistant ID: {p.get('assistantId', 'NONE ASSIGNED')}")
        print(f"  Server URL: {p.get('serverUrl', 'None')}")
        
        # Check if this is the 2nd number
        if p.get('id') == SECOND_PHONE_ID:
            print("\n  >>> THIS IS THE 2ND LINE <<<")
            if not p.get('assistantId'):
                print("  [!] No assistant assigned - will configure now")
else:
    print(f"Error: {res.status_code}")
    print(res.text)

print("\n" + "=" * 50)
print("LINKING JOHN TO 2ND PHONE NUMBER")
print("=" * 50)

# Update the 2nd phone number with John's assistant
update_url = f"https://api.vapi.ai/phone-number/{SECOND_PHONE_ID}"
update_payload = {
    "assistantId": JOHN_ASSISTANT_ID,
    "name": "John Roofing Line",
    "serverUrl": "https://nearmiss1193-afk--vapi-live.modal.run"
}

res = requests.patch(update_url, headers=headers, json=update_payload)

if res.status_code == 200:
    print("\n[SUCCESS] Phone configured!")
    result = res.json()
    print(f"  Number: {result.get('number')}")
    print(f"  Name: {result.get('name')}")
    print(f"  Assistant: {result.get('assistantId')}")
else:
    print(f"\n[ERROR] {res.status_code}")
    print(res.text)
