"""Quick Vapi test - minimal"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("VAPI_PRIVATE_KEY")

# Get first assistant
r = requests.get("https://api.vapi.ai/assistant", headers={"Authorization": f"Bearer {key}"})
assistants = r.json()
assistant_id = assistants[0]["id"] if assistants else None
print(f"Assistant: {assistants[0].get('name')} ({assistant_id[:20]})")

# Get first phone
r2 = requests.get("https://api.vapi.ai/phone-number", headers={"Authorization": f"Bearer {key}"})
phones = r2.json()
phone_id = phones[0]["id"] if phones else None
print(f"Phone: {phones[0].get('number')} ({phone_id})")

# Make call
payload = {
    "type": "outboundPhoneCall",
    "phoneNumberId": phone_id,
    "assistantId": assistant_id,
    "customer": {"number": "+13529368152"}
}

r3 = requests.post(
    "https://api.vapi.ai/call",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=payload
)

print(f"\nCall Status: {r3.status_code}")
if r3.status_code in [200, 201]:
    data = r3.json()
    print(f"SUCCESS! Call ID: {data.get('id')}")
else:
    print(f"Error: {r3.text}")
