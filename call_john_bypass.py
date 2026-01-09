# call_john_bypass.py
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
# Using Sarah's Phone ID (Verified)
PHONE_ID = "0401878d-697c-486d-883a-4d7a83d47dfc" 
# Using John's Assistant ID
ASSISTANT_ID = "78b4c14a-b44a-4096-82f5-a10106d1bfd2"
CUSTOMER_NUMBER = os.getenv("TEST_PHONE")

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "phoneNumberId": PHONE_ID,
    "assistantId": ASSISTANT_ID,
    "customer": {
        "number": CUSTOMER_NUMBER,
        "name": "Boss"
    },
    "assistantOverrides": {
        "firstMessage": "Hey, this is John. I'm calling from the main office line. Can you hear me alright?"
    }
}

print(f"Initiating John Bypass Call...")
print(f"Route: John Persona -> Sarah's Line ({PHONE_ID}) -> {CUSTOMER_NUMBER}")

res = requests.post("https://api.vapi.ai/call", headers=headers, json=payload)

if res.status_code == 201:
    print("Call Initiated Successfully!")
    print(json.dumps(res.json(), indent=2))
else:
    print(f"Error: {res.text}")
