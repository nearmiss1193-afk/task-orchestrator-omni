"""
FIX VAPI NOTIFICATION SYSTEM
Root cause: Sarah assistant has serverUrl: NONE and serverMessages: NOT SET
This script:
1. Sets serverUrl on Sarah's assistant to our Modal webhook
2. Sets serverMessages to include end-of-call-report
3. Also sets serverUrl on Sarah's phone number
4. Stores phone architecture knowledge
"""
import requests, os, json
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

# Sarah's assistant ID and phone number ID
SARAH_ASSISTANT_ID = "ae717f29-6542-422f-906f-ee7ba6fa0bfe"
SARAH_PHONE_ID = "86f73243-8916-4897-bd91-c066193c22b7"  # +19362984339

# Our Modal vapi_webhook endpoint
MODAL_WEBHOOK_URL = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"

# Phone architecture knowledge:
# +19362984339 = Vapi (calls only, cannot receive SMS)
# +15336 number = GHL/Lead Connector (SMS via website)

print("=== STEP 1: Update Sarah Assistant ===")
update_payload = {
    "serverUrl": MODAL_WEBHOOK_URL,
    "serverMessages": [
        "end-of-call-report",
        "status-update", 
        "assistant-request",
        "hang",
        "speech-update",
        "transcript"
    ]
}

r1 = requests.patch(
    f'https://api.vapi.ai/assistant/{SARAH_ASSISTANT_ID}',
    headers=headers,
    json=update_payload,
    timeout=15
)
print(f"Status: {r1.status_code}")
if r1.status_code == 200:
    data = r1.json()
    print(f"serverUrl: {data.get('serverUrl')}")
    print(f"serverMessages: {data.get('serverMessages')}")
    print("Sarah assistant FIXED")
else:
    print(f"ERROR: {r1.text[:200]}")

print("\n=== STEP 2: Update Sarah's Phone Number ===")
r2 = requests.patch(
    f'https://api.vapi.ai/phone-number/{SARAH_PHONE_ID}',
    headers=headers,
    json={"serverUrl": MODAL_WEBHOOK_URL},
    timeout=15
)
print(f"Status: {r2.status_code}")
if r2.status_code == 200:
    data2 = r2.json()
    print(f"Phone serverUrl: {data2.get('serverUrl')}")
    print("Phone number FIXED")
else:
    print(f"ERROR: {r2.text[:200]}")

print("\n=== STEP 3: Verify Config ===")
r3 = requests.get(f'https://api.vapi.ai/assistant/{SARAH_ASSISTANT_ID}', headers=headers, timeout=15)
a = r3.json()
print(f"Name: {a.get('name')}")
print(f"serverUrl: {a.get('serverUrl')}")
print(f"serverMessages: {a.get('serverMessages')}")

r4 = requests.get(f'https://api.vapi.ai/phone-number/{SARAH_PHONE_ID}', headers=headers, timeout=15)
p = r4.json()
print(f"Phone: {p.get('number')}")
print(f"Phone serverUrl: {p.get('serverUrl')}")

print("\n=== DONE ===")
print("Sarah's assistant now has:")
print(f"  serverUrl -> {MODAL_WEBHOOK_URL}")
print(f"  serverMessages -> includes end-of-call-report")
print("This means Vapi will now POST to our Modal webhook when calls end.")
print("Our vapi_webhook handler in deploy.py will process it.")
print("PLUS the heartbeat polling will catch any missed calls as backup.")
print("\nPhone architecture:")
print("  +19362984339 (Vapi) = CALLS ONLY, cannot receive SMS")
print("  GHL/Lead Connector 5336 number = SMS via website")
