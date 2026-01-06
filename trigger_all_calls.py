import os, requests, json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
USER_PHONE = os.getenv('TEST_PHONE')
PHONE_NUMBER_ID = os.getenv('VAPI_PHONE_NUMBER_ID')
ANTIGRAVITY_ID = "a3e439a2-4560-4625-99c8-222678bf130d"

def trigger_call(assistant_id, name):
    url = 'https://api.vapi.ai/call/phone'
    payload = {
        "assistantId": assistant_id,
        "phoneNumberId": PHONE_NUMBER_ID,
        "customer": {
            "number": USER_PHONE,
            "name": name
        }
    }
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        print(f"[{name}] Status: {res.status_code} | ID: {res.json().get('id') if res.status_code < 300 else res.text}")
        return res.json().get('id') if res.status_code < 300 else None
    except Exception as e:
        print(f"[{name}] Error: {e}")
        return None

print("--- STARTING LIVE EXECUTION ---")
trigger_call("1a797f12-e2dd-4f7f-b2c5-08c38c74859a", "Sarah 3.0")
trigger_call(ANTIGRAVITY_ID, "Antigravity")
