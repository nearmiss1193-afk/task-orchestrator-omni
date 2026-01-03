import json
import os
import requests
from dotenv import load_dotenv
import time

load_dotenv(".env.local")

def push_test_contact():
    token = os.environ.get("GHL_API_TOKEN")
    location_id = os.environ.get("GHL_LOCATION_ID")
    
    if not token or not location_id:
        print("❌ ERROR: GHL_API_TOKEN or GHL_LOCATION_ID missing")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    # Test Lead Data
    test_lead = {
        "firstName": "Spartan",
        "lastName": "Tester",
        "email": "spartantest@aiservico.com",
        "phone": "+15550199999", # Use a dummy phone number or user's real one for verification
        "locationId": location_id,
        "tags": ["trigger-vortex", "spartan-strike", "verification-test"],
        "customFields": [
            {"id": "W1QYZJ7ooiUtDiNmf9Xi", "value": "$1,200,000"}, # Annual Loss
            {"id": "JVka1qNEbJmPL4z31H1a", "value": "https://aiservico.com/audit-test"} # Audit Link
        ]
    }

    print(f"🚀 Pushing test contact to GHL...")
    
    try:
        res = requests.post("https://services.leadconnectorhq.com/contacts/", json=test_lead, headers=headers)
        if res.status_code in [200, 201]:
            contact_id = res.json().get("contact", {}).get("id")
            print(f"✅ TEST CONTACT CREATED: {contact_id}")
            print(f"🔗 Tag 'trigger-vortex' applied. Workflow should trigger now.")
            return contact_id
        else:
            print(f"⚠️ FAILED: {res.status_code} - {res.text}")
            return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    contact_id = push_test_contact()
    if contact_id:
        print("\n⏳ Waiting 10 seconds for GHL workflow to process...")
        time.sleep(10)
        print("🔍 Next step: Check GHL Conversations tab for sent SMS/Email.")
