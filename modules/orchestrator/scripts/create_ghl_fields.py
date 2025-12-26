import os
import requests
from dotenv import load_dotenv

env_path = r"c:\Users\nearm\.gemini\antigravity\scratch\task-orchestrator\.env.local"
load_dotenv(env_path)

def create_custom_fields():
    token = os.environ.get("GHL_API_TOKEN")
    location_id = os.environ.get("GHL_LOCATION_ID")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    fields_to_create = [
        {"name": "Annual Loss Projection", "dataType": "TEXT"},
        {"name": "Vortex Audit Link", "dataType": "TEXT"}
    ]

    url = f"https://services.leadconnectorhq.com/locations/{location_id}/customFields"
    
    for field in fields_to_create:
        try:
            res = requests.post(url, json=field, headers=headers)
            if res.status_code in [200, 201]:
                data = res.json().get("customField", {})
                print(f"✅ CREATED: {field['name']} (ID: {data.get('id')})")
            else:
                print(f"⚠️ FAILED to create {field['name']}: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"❌ Error creating {field['name']}: {str(e)}")

if __name__ == "__main__":
    create_custom_fields()
