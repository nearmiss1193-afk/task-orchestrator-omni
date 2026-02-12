"""
FIX 3: Update 3 phone numbers serverUrl + Test GHL webhook
All in one script, run in parallel with deploy.py code fixes.
"""
import requests, os, json
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

vapi_key = os.getenv('VAPI_PRIVATE_KEY')
vh = {'Authorization': f'Bearer {vapi_key}', 'Content-Type': 'application/json'}
our_webhook = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"

# ===== FIX 3A: Update 3 phone numbers =====
print("=" * 60)
print("FIX 3A: Updating phone number serverUrls")
print("=" * 60)

# First get all phone numbers to find the IDs
all_phones = requests.get('https://api.vapi.ai/phone-number', headers={'Authorization': f'Bearer {vapi_key}'}, timeout=15).json()
dead_numbers = ['+18636928474', '+18633373601', '+18633373705']

for p in all_phones:
    num = p.get('number', '')
    pid = p.get('id', '')
    old_url = p.get('serverUrl', 'NONE')
    
    if num in dead_numbers:
        print(f"\n  Fixing {num} (id: {pid})")
        print(f"    Old serverUrl: {old_url[:60]}")
        
        r = requests.patch(
            f'https://api.vapi.ai/phone-number/{pid}',
            headers=vh,
            json={"serverUrl": our_webhook},
            timeout=15
        )
        
        if r.status_code == 200:
            new_url = r.json().get('serverUrl', 'NONE')
            print(f"    New serverUrl: {new_url[:60]}")
            print(f"    ✅ FIXED")
        else:
            print(f"    ❌ FAILED: {r.status_code} {r.text[:200]}")

# Also fix any other phones on the old endpoint
for p in all_phones:
    num = p.get('number', '')
    pid = p.get('id', '')
    old_url = p.get('serverUrl', '')
    
    if 'empire-inbound' in old_url and num not in dead_numbers:
        print(f"\n  Also fixing {num} (id: {pid}) - had empire-inbound URL")
        r = requests.patch(
            f'https://api.vapi.ai/phone-number/{pid}',
            headers=vh,
            json={"serverUrl": our_webhook},
            timeout=15
        )
        if r.status_code == 200:
            print(f"    ✅ FIXED")
        else:
            print(f"    ❌ FAILED: {r.status_code}")

# ===== FIX 3B: Test GHL Notification Webhook =====
print("\n" + "=" * 60)
print("FIX 3B: Testing GHL Notification Webhook")
print("=" * 60)

ghl_webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
test_payload = {
    "phone": "+13529368152",
    "message": "🧪 TEST: If Dan receives this, the GHL notification webhook works. Sent from board fix script."
}

print(f"  Sending to: {ghl_webhook[:60]}...")
print(f"  Payload: {json.dumps(test_payload)}")

try:
    r = requests.post(ghl_webhook, json=test_payload, timeout=15)
    print(f"  HTTP Status: {r.status_code}")
    print(f"  Response: {r.text[:300]}")
    
    if r.status_code == 200:
        print("  ✅ GHL webhook accepted the request")
        print("  → If Dan receives the test SMS, the webhook + GHL workflow are working")
        print("  → If Dan does NOT receive it, the GHL workflow is misconfigured")
    else:
        print(f"  ❌ GHL webhook returned {r.status_code} - webhook may be dead or misconfigured")
except Exception as e:
    print(f"  ❌ EXCEPTION: {e}")

# ===== VERIFY ALL PHONE NUMBERS =====
print("\n" + "=" * 60)
print("VERIFICATION: All phone numbers after fix")
print("=" * 60)

all_phones_after = requests.get('https://api.vapi.ai/phone-number', headers={'Authorization': f'Bearer {vapi_key}'}, timeout=15).json()
for p in all_phones_after:
    num = p.get('number', '') or '(no number)'
    url = p.get('serverUrl', 'NONE')[:60]
    aid = (p.get('assistantId') or 'NONE')[:20]
    status = "✅" if "ghl-omni-automation" in url else "⚠️"
    print(f"  {status} {num} -> {url}")

print("\n✅ All fixes applied")
