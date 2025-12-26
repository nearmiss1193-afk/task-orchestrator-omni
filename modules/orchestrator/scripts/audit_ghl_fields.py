import os
import requests
from dotenv import load_dotenv

env_path = r"c:\Users\nearm\.gemini\antigravity\scratch\task-orchestrator\.env.local"
load_dotenv(env_path)

def audit_custom_fields():
    token = os.environ.get("GHL_API_TOKEN")
    location_id = os.environ.get("GHL_LOCATION_ID")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28"
    }

    url = f"https://services.leadconnectorhq.com/locations/{location_id}/customFields"
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            fields = res.json().get("customFields", [])
            print(f"📋 Found {len(fields)} custom fields.")
            target_fields = ["annual_loss_projection", "vortex_audit_link"]
            found = []
            for f in fields:
                print(f"FIELD: {f.get('name')} | ID: {f.get('id')}")
            
            for t in target_fields:
                if not any(t in f for f in found):
                    print(f"❌ MISSING: {t}")
        else:
            print(f"❌ API Error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    audit_custom_fields()
