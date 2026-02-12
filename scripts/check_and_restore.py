"""Check webhook.site for results and restore serverUrl immediately"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

# Load config
with open('scripts/webhook_test_token.json', 'r') as f:
    config = json.load(f)

uuid = config['uuid']
original_url = config['original_server_url']

# Check webhook.site
print("=== WEBHOOK.SITE RESULTS ===")
r = requests.get(f'https://webhook.site/token/{uuid}/requests', timeout=10)
data = r.json()
total = data.get('total', 0)
print(f"Total requests received: {total}")

if total > 0:
    print("\nVAPI IS SENDING WEBHOOKS -- problem is on Modal's end")
    for req in data.get('data', []):
        print(f"\nMethod: {req.get('method')}")
        print(f"Time: {req.get('created_at')}")
        content = req.get('content', '')
        if content:
            try:
                parsed = json.loads(content)
                msg = parsed.get('message', {})
                print(f"Event: {msg.get('type', 'unknown')}")
                call = msg.get('call', {})
                print(f"CallId: {call.get('id', '?')}")
                cust = call.get('customer', {})
                print(f"Customer: {cust.get('number', '?')}")
                print(f"Content (first 300 chars): {content[:300]}")
            except:
                print(f"Raw: {content[:300]}")
else:
    print("\nNO REQUESTS RECEIVED -- Vapi is NOT sending webhooks (known Dec 2025 bug)")
    print("Recommendation: Use Option C (Make.com bypass) or contact Vapi support")

# ALWAYS restore serverUrl
print("\n=== RESTORING ORIGINAL SERVERURL ===")
vapi_key = os.getenv('VAPI_PRIVATE_KEY')
headers = {
    'Authorization': f'Bearer {vapi_key}',
    'Content-Type': 'application/json'
}

r2 = requests.patch(f"https://api.vapi.ai/assistant/{config['assistant_id']}", headers=headers, json={
    'serverUrl': original_url
})
print(f"Assistant restore: {r2.status_code}")

r3 = requests.patch(f"https://api.vapi.ai/phone-number/{config['phone_id']}", headers=headers, json={
    'serverUrl': original_url
})
print(f"Phone restore: {r3.status_code}")
print(f"Restored to: {original_url}")
