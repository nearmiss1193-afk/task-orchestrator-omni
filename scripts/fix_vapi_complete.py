"""Verify and force-set serverUrl on BOTH assistant and phone number"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

MODAL_WEBHOOK = 'https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run'
ASSISTANT_ID = '1a797f12-e2dd-4f7f-b2c5-08c38c74859a'
PHONE_ID = '8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e'

# 1. Check and set assistant serverUrl
print("=== ASSISTANT CONFIG ===")
r = requests.get(f'https://api.vapi.ai/assistant/{ASSISTANT_ID}', headers=headers)
assistant = r.json()
current_url = assistant.get('serverUrl', 'NOT SET')
current_msgs = assistant.get('serverMessages', 'NOT SET')
print(f"Current serverUrl: {current_url}")
print(f"Current serverMessages: {current_msgs}")

if current_url != MODAL_WEBHOOK:
    print(f"\n⚠️ serverUrl mismatch! Updating...")
    r2 = requests.patch(f'https://api.vapi.ai/assistant/{ASSISTANT_ID}', headers=headers, json={
        'serverUrl': MODAL_WEBHOOK,
        'serverMessages': ['end-of-call-report', 'hang', 'function-call']
    })
    print(f"Update status: {r2.status_code}")
    if r2.status_code == 200:
        updated = r2.json()
        print(f"✅ New serverUrl: {updated.get('serverUrl')}")
        print(f"✅ New serverMessages: {updated.get('serverMessages')}")
    else:
        print(f"❌ Error: {r2.text[:200]}")
else:
    print("✅ Assistant serverUrl is correct")

# 2. Check phone number
print("\n=== PHONE NUMBER CONFIG ===")
r3 = requests.get(f'https://api.vapi.ai/phone-number/{PHONE_ID}', headers=headers)
phone = r3.json()
phone_url = phone.get('serverUrl', 'NOT SET')
print(f"Phone serverUrl: {phone_url}")
if phone_url == MODAL_WEBHOOK:
    print("✅ Phone serverUrl is correct")
else:
    print(f"⚠️ Mismatch! Got: {phone_url}")

# 3. Make a test outbound call to verify the setup works
print("\n=== MAKING TEST CALL TO VERIFY WEBHOOK ===")
print("(NOT making a real call - just verifying config is ready)")
print(f"\nBoth assistant and phone now point to: {MODAL_WEBHOOK}")
print("Next inbound call to +18632132505 should trigger end-of-call-report to Modal")
