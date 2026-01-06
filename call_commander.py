#!/usr/bin/env python3
"""Trigger Sarah to call the Commander"""
import requests
import os

# Get Vapi key from environment or use direct
VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY", "")

# Sarah's assistant ID
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
COMMANDER_PHONE = "+13529368152"

if not VAPI_KEY:
    # Try reading from .env manually
    try:
        with open('.env', 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('VAPI_PRIVATE_KEY='):
                    VAPI_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    except: pass

if not VAPI_KEY:
    print("ERROR: No VAPI_PRIVATE_KEY found")
    exit(1)

print(f"Calling {COMMANDER_PHONE} with Sarah...")
print(f"Using key: {VAPI_KEY[:20]}...")

response = requests.post(
    "https://api.vapi.ai/call/phone",
    json={
        "assistantId": SARAH_ID,
        "customer": {
            "number": COMMANDER_PHONE
        }
    },
    headers={
        "Authorization": f"Bearer {VAPI_KEY}",
        "Content-Type": "application/json"
    }
)

print(f"\nStatus: {response.status_code}")
if response.status_code in [200, 201]:
    data = response.json()
    print(f"✅ SUCCESS! Call initiated")
    print(f"Call ID: {data.get('id', 'unknown')}")
else:
    print(f"❌ FAILED: {response.text}")
