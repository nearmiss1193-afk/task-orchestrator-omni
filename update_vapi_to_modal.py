"""
Update Vapi phone numbers to point to Modal webhook
"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

# The new Modal webhook URL
MODAL_WEBHOOK = "https://nearmiss1193-afk--empire-inbound-vapi-webhook.modal.run"

print("="*60)
print("UPDATING VAPI PHONE NUMBERS TO USE MODAL WEBHOOK")
print("="*60)
print(f"New serverUrl: {MODAL_WEBHOOK}")

# Get all phone numbers
r = requests.get('https://api.vapi.ai/phone-number', headers=headers)
phones = r.json()

updated = 0
for p in phones:
    num = p.get('number')
    phone_id = p.get('id')
    current_url = p.get('serverUrl', 'none')
    
    print(f"\n{num}:")
    print(f"  Current serverUrl: {current_url}")
    
    # Update serverUrl to Modal
    update = requests.patch(
        f"https://api.vapi.ai/phone-number/{phone_id}",
        headers=headers,
        json={"serverUrl": MODAL_WEBHOOK}
    )
    
    if update.ok:
        print(f"  UPDATED to Modal webhook")
        updated += 1
    else:
        print(f"  ERROR: {update.status_code}")

print("\n" + "="*60)
print(f"Updated {updated} phone numbers to use Modal webhook")
print("="*60)

# Also update Sarah assistant
print("\nUpdating Sarah assistant serverUrl...")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

update = requests.patch(
    f"https://api.vapi.ai/assistant/{SARAH_ID}",
    headers=headers,
    json={
        "serverUrl": MODAL_WEBHOOK,
        "server": {"url": MODAL_WEBHOOK, "timeoutSeconds": 20}
    }
)

if update.ok:
    print("  Sarah updated!")
else:
    print(f"  ERROR: {update.status_code} - {update.text[:100]}")
