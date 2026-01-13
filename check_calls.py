"""Check recent Vapi calls to see why Sarah hung up"""
import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}'}

print("="*60)
print("RECENT VAPI CALLS")
print("="*60)

r = requests.get('https://api.vapi.ai/call?limit=10', headers=headers)
calls = r.json()

for c in calls[:5]:
    print(f"\nCall ID: {c.get('id','?')[:12]}...")
    print(f"  Type: {c.get('type','?')}")
    print(f"  Status: {c.get('status','?')}")
    print(f"  Ended Reason: {c.get('endedReason','?')}")
    print(f"  Duration: {c.get('duration',0)} seconds")
    print(f"  Customer: {c.get('customer',{}).get('number','?')}")
    print(f"  Created: {c.get('createdAt','?')}")
    
    # Get more details
    if c.get('endedReason') in ['assistant-ended-call', 'silence-timed-out', 'customer-did-not-answer']:
        print(f"  --> ISSUE: {c.get('endedReason')}")

print("\n" + "="*60)

# Get latest call full details
if calls:
    latest = calls[0]
    print("\nLATEST CALL DETAILS:")
    print(json.dumps(latest, indent=2)[:2000])
