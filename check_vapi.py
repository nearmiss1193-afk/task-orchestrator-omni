"""
Check Vapi Configuration - List Assistants and Phone Numbers
"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("VAPI_PRIVATE_KEY")
print(f"API Key: {key[:10]}..." if key else "NO KEY")

# List assistants
print("\n=== ASSISTANTS ===")
r = requests.get("https://api.vapi.ai/assistant", headers={"Authorization": f"Bearer {key}"})
if r.status_code == 200:
    for a in r.json()[:10]:
        print(f"  {a.get('id')} - {a.get('name')}")
else:
    print(f"Error: {r.status_code} - {r.text[:200]}")

# List phone numbers
print("\n=== PHONE NUMBERS ===")
r2 = requests.get("https://api.vapi.ai/phone-number", headers={"Authorization": f"Bearer {key}"})
if r2.status_code == 200:
    for p in r2.json()[:10]:
        print(f"  {p.get('id')} - {p.get('number')}")
else:
    print(f"Error: {r2.status_code} - {r2.text[:200]}")
