import os, requests, json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = os.getenv('VAPI_PHONE_NUMBER_ID') # Corrected from VAPI_PHONE_ID
ASSISTANT_ID = "a3e439a2-4560-4625-99c8-222678bf130d" # Hardcoded from call_antigravity.py
TEST_PHONE = os.getenv('TEST_PHONE')

print(f"Key: {VAPI_PRIVATE_KEY[:5]}...")
print(f"Phone ID: {VAPI_PHONE_ID}")
print(f"Assistant: {ASSISTANT_ID}")
print(f"Target: {TEST_PHONE}")

def force_call():
    phone = f"+1{TEST_PHONE.replace('-', '').replace(' ', '')[-10:]}"
    print(f"dialing {phone}...")
    
    url = "https://api.vapi.ai/call"
    payload = {
        "type": "outboundPhoneCall",
        "phoneNumberId": VAPI_PHONE_ID,
        "assistantId": ASSISTANT_ID,
        "customer": {
            "number": phone,
            "name": "Force Test User"
        }
    }
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    force_call()
