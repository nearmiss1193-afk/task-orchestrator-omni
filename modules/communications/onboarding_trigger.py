import sys
import os
import json
import requests
from datetime import datetime
from .sms import send_sms

# Path to local DB
DB_PATH = os.path.join(os.path.dirname(__file__), '../../db/clients.json')

# Vapi Config
VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY") or "c23c884d-0008-4b14-ad5d-530e98d0c9da"
ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"
# Placeholder: The script 'fetch_vapi_phones.py' returned no numbers.
# You must buy a number in Vapi Dashboard or Import Twilio to make this work.
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID") 

def trigger_outbound_call(customer_phone, customer_name):
    """
    Initiates an immediate outbound call to the new lead using Vapi.
    """
    if not VAPI_PHONE_NUMBER_ID:
        print(f"⚠️  SKIPPING OUTBOUND CALL: No VAPI_PHONE_NUMBER_ID configured.")
        return False

    url = "https://api.vapi.ai/call/phone"
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "assistantId": ASSISTANT_ID,
        "customer": {
            "number": customer_phone,
            "name": customer_name
        }
    }
    
    try:
        print(f"📞 Initiating Vapi Call to {customer_name} ({customer_phone})...")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"✅ Call Initiated: {response.json().get('id')}")
        return True
    except Exception as e:
        print(f"❌ Vapi Call Failed: {e}")
        if response:
            print(f"   Response: {response.text}")
        return False

def onboard_lead(data):
    """
    Saves lead to local JSON DB and triggers onboarding actions.
    """
    print(f"🚀 Onboarding Lead: {data}")
    
    # 1. Load DB
    try:
        with open(DB_PATH, 'r') as f:
            clients = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        clients = []
        
    # 2. Add Client
    new_client = {
        "id": f"lead_{len(clients) + 1}",
        "name": data.get('name'),
        "phone": data.get('phone'),
        "email": data.get('email'),
        "industry": data.get('industry', 'General'),
        "status": "New",
        "created_at": datetime.now().isoformat()
    }
    clients.append(new_client)
    
    # 3. Save DB
    with open(DB_PATH, 'w') as f:
        json.dump(clients, f, indent=2)
    print("✅ Welcome SMS Sent")

if __name__ == "__main__":
    # stored in modules/communications, so we need to fix path if running directly or imported
    # Typically called from root
    if len(sys.argv) < 3:
        print("Usage: python onboarding_trigger.py <phone> <name> <industry>")
        sys.exit(1)
    
    trigger_onboarding(sys.argv[1], sys.argv[2], sys.argv[3])
