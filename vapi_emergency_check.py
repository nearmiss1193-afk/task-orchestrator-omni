"""
EMERGENCY FIX - Get Vapi phone numbers and assistant configs
"""
import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}'}

print("="*60)
print("VAPI EMERGENCY DIAGNOSTIC")
print("="*60)

# Get phone numbers
print("\nPHONE NUMBERS:")
r = requests.get('https://api.vapi.ai/phone-number', headers=headers)
phones = r.json()
for p in phones:
    print(f"\nNumber: {p.get('number')}")
    print(f"  ID: {p.get('id')}")
    print(f"  Assistant ID: {p.get('assistantId', 'NONE')}")
    print(f"  SMS Enabled: {p.get('smsEnabled', False)}")
    print(f"  Status: {p.get('status')}")

# Get assistants
print("\n" + "-"*60)
print("ASSISTANTS:")
r = requests.get('https://api.vapi.ai/assistant', headers=headers)
assistants = r.json()
for a in assistants:
    print(f"\nName: {a.get('name')}")
    print(f"  ID: {a.get('id')}")
    print(f"  Model: {a.get('model', {}).get('model', 'unknown')}")

# Check if phone has assistant assigned
print("\n" + "="*60)
print("DIAGNOSIS:")
for p in phones:
    if not p.get('assistantId'):
        print(f"WARNING: {p.get('number')} has NO ASSISTANT - calls won't be answered!")
    else:
        print(f"OK: {p.get('number')} -> {p.get('assistantId')[:12]}...")
    if not p.get('smsEnabled'):
        print(f"WARNING: {p.get('number')} SMS is DISABLED!")

print("="*60)

# Write to file for viewing
with open('vapi_diagnostic.json', 'w') as f:
    json.dump({'phones': phones, 'assistants': assistants}, f, indent=2)
print("\nFull data saved to vapi_diagnostic.json")
