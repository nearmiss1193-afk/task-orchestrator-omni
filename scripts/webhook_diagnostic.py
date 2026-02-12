"""
Webhook.site diagnostic: Temporarily point Vapi assistant serverUrl 
to webhook.site, then Dan makes a test call.
If webhook.site receives data = Modal is the problem.
If webhook.site receives nothing = Vapi is the problem.
"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

ASSISTANT_ID = '1a797f12-e2dd-4f7f-b2c5-08c38c74859a'
PHONE_ID = '8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e'

# Step 1: Create a webhook.site token
print("=== Creating webhook.site test URL ===")
r = requests.post('https://webhook.site/token', timeout=10)
token_data = r.json()
test_url = f"https://webhook.site/{token_data['uuid']}"
token_uuid = token_data['uuid']
print(f"Test URL: {test_url}")
print(f"UUID: {token_uuid}")

# Step 2: Point assistant serverUrl to webhook.site
print("\n=== Updating assistant serverUrl to webhook.site ===")
r2 = requests.patch(f'https://api.vapi.ai/assistant/{ASSISTANT_ID}', headers=headers, json={
    'serverUrl': test_url
})
print(f"Assistant update: {r2.status_code}")
if r2.status_code == 200:
    print(f"New serverUrl: {r2.json().get('serverUrl')}")

# Step 3: Also update phone number
print("\n=== Updating phone number serverUrl to webhook.site ===")
r3 = requests.patch(f'https://api.vapi.ai/phone-number/{PHONE_ID}', headers=headers, json={
    'serverUrl': test_url
})
print(f"Phone update: {r3.status_code}")
if r3.status_code == 200:
    print(f"New phone serverUrl: {r3.json().get('serverUrl')}")

# Save the token so we can check it later and restore
with open('scripts/webhook_test_token.json', 'w') as f:
    json.dump({
        'uuid': token_uuid,
        'test_url': test_url,
        'original_server_url': 'https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run',
        'assistant_id': ASSISTANT_ID,
        'phone_id': PHONE_ID,
    }, f, indent=2)

print("\n=== INSTRUCTIONS ===")
print("1. Call Sarah at +1 (863) 213-2505")
print("2. Talk for at least 15-20 seconds")
print("3. Then run check_webhook_results.py to see if Vapi sent data")
print(f"\nOr check manually: https://webhook.site/#!/view/{token_uuid}")
