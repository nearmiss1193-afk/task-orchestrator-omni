"""Check latest Vapi calls to see if serverUrl fix is active"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}'}

# Get the most recent calls
r = requests.get('https://api.vapi.ai/call?limit=3', headers=headers)
calls = r.json()

print("=== LATEST VAPI CALLS ===")
for c in calls:
    print(json.dumps({
        'id': c.get('id', '?'),
        'status': c.get('status'),
        'duration': c.get('duration', 0),
        'endedReason': c.get('endedReason', '?'),
        'created': c.get('createdAt', '?')[:19],
        'customer': c.get('customer', {}).get('number', '?'),
        'serverUrl': c.get('serverUrl', 'NULL'),
        'phoneNumberId': c.get('phoneNumberId', '?'),
        'assistantId': c.get('assistantId', '?')[:20],
    }, indent=2))
    print()

# Also check the phone number config to confirm fix persisted
print("\n=== SARAH PHONE CONFIG ===")
r2 = requests.get('https://api.vapi.ai/phone-number', headers=headers)
for p in r2.json():
    if p.get('number') == '+18632132505':
        print(f"ID: {p.get('id')}")
        print(f"serverUrl: {p.get('serverUrl', 'NOT SET')}")
        print(f"assistantId: {p.get('assistantId', 'NOT SET')}")
        break
