"""Check webhook.site for any requests received, then restore original serverUrl"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

# Load saved config
with open('scripts/webhook_test_token.json', 'r') as f:
    config = json.load(f)

uuid = config['uuid']
original_url = config['original_server_url']
assistant_id = config['assistant_id']
phone_id = config['phone_id']

# Check webhook.site for requests
print("=== Checking webhook.site for received requests ===")
r = requests.get(f'https://webhook.site/token/{uuid}/requests', timeout=10)
requests_data = r.json()

total = requests_data.get('total', 0)
print(f"Total requests received: {total}")

if total > 0:
    for req in requests_data.get('data', []):
        print(f"\n--- Request ---")
        print(f"Method: {req.get('method')}")
        print(f"Created: {req.get('created_at')}")
        content = req.get('content', '')
        if content:
            try:
                parsed = json.loads(content)
                event = parsed.get('message', {}).get('type', 'unknown')
                print(f"Event type: {event}")
                print(f"Content preview: {json.dumps(parsed, indent=2)[:500]}")
            except:
                print(f"Raw content: {content[:500]}")
        print()
else:
    print("No requests received yet.")
    print("Dan needs to call Sarah and hang up for the end-of-call-report to fire.")

# Restore original serverUrl
print("\n=== Restoring original serverUrl ===")
vapi_key = os.getenv('VAPI_PRIVATE_KEY')
headers = {
    'Authorization': f'Bearer {vapi_key}',
    'Content-Type': 'application/json'
}

restore = input("Restore original serverUrl now? (y/n): ").strip().lower()
if restore == 'y':
    # Restore assistant
    r2 = requests.patch(f'https://api.vapi.ai/assistant/{assistant_id}', headers=headers, json={
        'serverUrl': original_url
    })
    print(f"Assistant restore: {r2.status_code}")
    
    # Restore phone
    r3 = requests.patch(f'https://api.vapi.ai/phone-number/{phone_id}', headers=headers, json={
        'serverUrl': original_url
    })
    print(f"Phone restore: {r3.status_code}")
    print(f"Restored to: {original_url}")
else:
    print("Skipped restore. Run this script again to restore later.")
