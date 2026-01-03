import os
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

h = {
    'Authorization': f'Bearer {os.environ.get("GHL_API_TOKEN")}',
    'Version': '2021-07-28',
    'Content-Type': 'application/json'
}
p = {
    'locationId': os.environ.get("GHL_LOCATION_ID"),
    'query': 'owner@aiserviceco.com'
}

def setup_owner():
    # Search for existing contact by email
    email = 'owner@aiserviceco.com'
    url = f'https://services.leadconnectorhq.com/contacts/?locationId={os.environ.get("GHL_LOCATION_ID")}&email={email}'
    r = requests.get(url, headers=h)
    data = r.json()
    
    contact_id = None
    if data.get('contacts'):
        contact_id = data['contacts'][0]['id']
        print(f"✅ Owner found: {contact_id}")
    else:
        print("Owner not found. Creating contact...")
        cp = {
            'locationId': os.environ.get("GHL_LOCATION_ID"),
            'email': 'owner@aiserviceco.com',
            'firstName': 'Owner',
            'lastName': 'Admin'
        }
        cr = requests.post('https://services.leadconnectorhq.com/contacts/', json=cp, headers=h)
        if cr.status_code in [200, 201]:
            contact_id = cr.json().get('contact', {}).get('id')
            print(f"✅ Owner created: {contact_id}")
        else:
            print(f"❌ Failed to create owner: {cr.text}")
            
    if contact_id:
        with open("owner_config.json", "w") as f:
            json.dump({"contact_id": contact_id}, f)
        print("✅ owner_config.json updated.")

if __name__ == "__main__":
    import json
    setup_owner()
