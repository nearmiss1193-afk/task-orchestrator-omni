# simple_call_check.py
import os
import requests
from dotenv import load_dotenv
load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

print("LAST 5 CALL ATTEMPTS:")
print("-" * 60)

r = requests.get("https://api.vapi.ai/call?limit=5", headers=headers)
if r.status_code == 200:
    for c in r.json():
        call_id = c.get('id', 'Unknown')[:15]
        status = c.get('status', 'Unknown')
        reason = c.get('endedReason', 'N/A')
        phone = c.get('customer', {}).get('number', 'Unknown')
        created = c.get('createdAt', '')[:19]
        
        print(f"ID: {call_id}...")
        print(f"  To: {phone}")
        print(f"  Status: {status}")
        print(f"  Ended Because: {reason}")
        print(f"  Created: {created}")
        print("-" * 40)
else:
    print(f"Error: {r.status_code}")
