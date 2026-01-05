
import os
import requests
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")

print("=== VAPI CALL TEST (FULL ERROR) ===")
print(f"Key: {VAPI_KEY[:10]}...")

headers = {
    'Authorization': f'Bearer {VAPI_KEY}',
    'Content-Type': 'application/json'
}

# Use the exact IDs from the screenshot
payload = {
    "phoneNumberId": "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e",
    "customer": {
        "number": "+13529368152",
        "name": "Commander"
    },
    "assistantId": "8a7f18bf-8c1e-4eaf-afdd-7a8339f40079"  # This might be wrong
}

print(f"\nPayload:\n{json.dumps(payload, indent=2)}")

print("\nSending call request...")
res = requests.post("https://api.vapi.ai/call/phone", json=payload, headers=headers)

print(f"Status: {res.status_code}")
print(f"Response:\n{res.text}")

# Also get assistants list
print("\n\n=== ASSISTANT LIST ===")
res2 = requests.get("https://api.vapi.ai/assistant", headers=headers)
if res2.status_code == 200:
    assistants = res2.json()
    for a in assistants[:5]:
        print(f"  ID: {a.get('id')}")
        print(f"  Name: {a.get('name')}")
        print("  ---")
else:
    print(f"Error: {res2.text}")
