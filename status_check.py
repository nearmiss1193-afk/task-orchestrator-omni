import requests
import os
from dotenv import load_dotenv
load_dotenv()

print("="*50)
print("CURRENT STATUS CHECK")
print("="*50)

# Check Vapi calls
print("\n📞 VAPI CALL STATUS:")
key = os.getenv('VAPI_PRIVATE_KEY')
if key:
    try:
        r = requests.get('https://api.vapi.ai/call', headers={'Authorization': f'Bearer {key}'}, timeout=10)
        if r.ok:
            calls = r.json()
            print(f"   Total calls in history: {len(calls)}")
            recent = [c for c in calls if '2026-01-13' in c.get('createdAt', '')]
            print(f"   Calls TODAY (Jan 13): {len(recent)}")
            if recent:
                print("   Recent calls:")
                for c in recent[-5:]:
                    status = c.get('status', '?')
                    number = c.get('customer', {}).get('number', '?')
                    created = c.get('createdAt', '?')[:16]
                    print(f"     [{status}] {number} | {created}")
        else:
            print(f"   API Error: {r.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
else:
    print("   Missing VAPI_PRIVATE_KEY")

# Check if we sent any emails via webhook
print("\n📧 WEBHOOK STATUS:")
print("   Test email sent to owner@aiserviceco.com earlier")
print("   Check inbox for verification")

print("\n" + "="*50)
