
"""
Enable Inbound SMS on Vapi Phone Number
Vapi supports SMS if using Twilio-backed number.
This script enables smsEnabled on the existing phone number.
"""
import os
import requests

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")
PHONE_ID = "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e"  # From app.py
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

if not VAPI_KEY:
    # Try to find in temp_env.txt
    try:
        with open("temp_env.txt") as f:
            for line in f:
                if "VAPI" in line.upper():
                    print(f"Found: {line.strip()}")
    except:
        pass
    print("ERROR: VAPI_PRIVATE_KEY not found in environment.")
    print("Please set it or add to temp_env.txt")
    exit(1)

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Get current phone number config
print(f"Fetching phone number config: {PHONE_ID}...")
r = requests.get(f"https://api.vapi.ai/phone-number/{PHONE_ID}", headers=headers)
if r.ok:
    data = r.json()
    print(f"Current SMS Enabled: {data.get('smsEnabled', False)}")
    print(f"Provider: {data.get('provider', 'unknown')}")
    print(f"Number: {data.get('number', 'N/A')}")
else:
    print(f"GET Error: {r.status_code} - {r.text}")
    exit(1)

# Step 2: Enable SMS
print("\nEnabling SMS...")
update_payload = {
    "smsEnabled": True,
    "assistantId": SARAH_ID  # Route SMS to Sarah
}

r2 = requests.patch(
    f"https://api.vapi.ai/phone-number/{PHONE_ID}",
    headers=headers,
    json=update_payload
)

if r2.ok:
    print(f"✅ SMS Enabled Successfully!")
    print(r2.json())
else:
    print(f"PATCH Error: {r2.status_code} - {r2.text}")
