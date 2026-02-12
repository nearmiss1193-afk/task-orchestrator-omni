"""Fix Sarah's phone number in Vapi - set serverUrl for end-of-call webhook"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

# Update config for serverUrl
update = {
    'serverUrl': 'https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run',
    'serverMessages': ['end-of-call-report', 'hang', 'function-call']
}

# Find Sarah's phone (+18632132505)
r = requests.get('https://api.vapi.ai/phone-number', headers=headers)
phones = r.json()
sarah_phone = None
for p in phones:
    if p.get('number') == '+18632132505':
        sarah_phone = p
        break

if sarah_phone:
    full_id = sarah_phone['id']
    print(f"Found Sarah phone: {full_id}")
    current_url = sarah_phone.get('serverUrl', 'NOT SET')
    print(f"Current serverUrl: {current_url}")
    
    # PATCH to update
    r2 = requests.patch(
        f'https://api.vapi.ai/phone-number/{full_id}', 
        headers=headers, 
        json=update
    )
    print(f"Update status: {r2.status_code}")
    print(f"Full response: {r2.text}")
else:
    print("ERROR: Could not find phone +18632132505")
