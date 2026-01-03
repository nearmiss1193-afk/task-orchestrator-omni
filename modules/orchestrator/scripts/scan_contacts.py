import os
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

h = {
    'Authorization': f'Bearer {os.environ.get("GHL_API_TOKEN")}',
    'Version': '2021-07-28',
    'Content-Type': 'application/json'
}

def find_owner_id():
    url = f'https://services.leadconnectorhq.com/contacts/?locationId={os.environ.get("GHL_LOCATION_ID")}&limit=100'
    r = requests.get(url, headers=h)
    data = r.json()
    
    for contact in data.get('contacts', []):
        if contact.get('email') == 'owner@aiserviceco.com':
            return contact.get('id')
    return None

if __name__ == "__main__":
    owner_id = find_owner_id()
    if owner_id:
        print(f"✅ Found Owner ID: {owner_id}")
        import json
        with open("owner_config.json", "w") as f:
            json.dump({"contact_id": owner_id}, f)
    else:
        print("❌ Owner not found in the first 100 contacts.")
