import os
import requests
from dotenv import load_dotenv

env_path = r"c:\Users\nearm\.gemini\antigravity\scratch\task-orchestrator\.env.local"
load_dotenv(env_path)

def fire_test_contact():
    token = os.environ.get("GHL_API_TOKEN")
    location_id = os.environ.get("GHL_LOCATION_ID")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    # Fetch mapping for target IDs
    annual_loss_id = "W1QYZJ7ooiUtDiNmf9Xi"
    audit_link_id = "JVka1qNEbJmPL4z31H1a"

    payload = {
        "firstName": "Vortex",
        "lastName": "Test (Spartan Alpha)",
        "email": "vortex-test@aiservico.com",
        "phone": "+15550109999",
        "locationId": location_id,
        "tags": ["trigger-vortex", "spartan-strike"],
        "customFields": [
            {"id": annual_loss_id, "value": "$1,250,000"},
            {"id": audit_link_id, "value": "https://aiservico.com/audit/vortex-test"}
        ]
    }

    url = "https://services.leadconnectorhq.com/contacts/"
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code in [200, 201]:
            print(f"✅ TEST CONTACT CREATED: {res.json().get('contact', {}).get('id')}")
            print("🕒 Waiting 10 seconds for automation to trigger...")
        else:
            print(f"⚠️ FAILED to create test contact: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    fire_test_contact()
