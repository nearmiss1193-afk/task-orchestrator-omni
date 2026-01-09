
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GHL_TOKEN = os.getenv("GHL_AGENCY_API_TOKEN") # Using Agency API Token based on other scripts
# Or maybe generic API key
GHL_LOC = os.getenv("GHL_LOCATION_ID")

# Fallback keys commonly used in this repo
if not GHL_TOKEN:
    GHL_TOKEN = os.getenv("GHL_API_KEY")

headers = {
    'Authorization': f'Bearer {GHL_TOKEN}',
    'Version': '2021-07-28',
    'Content-Type': 'application/json',
    'Location-Id': GHL_LOC
}

def check_owner():
    email = "owner@aiserviceco.com"
    print(f"Searching for {email} in GHL...")
    
    url = f"https://services.leadconnectorhq.com/contacts/search?query={email}"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            contacts = data.get('contacts', [])
            if contacts:
                print(f"✅ Found Owner: {contacts[0]['id']}")
                return contacts[0]['id']
            else:
                print("❌ Owner not found. Creating...")
                return create_owner(email)
        else:
            print(f"❌ Error searching: {r.status_code} {r.text}")
    except Exception as e:
         print(f"❌ Exception: {e}")

def create_owner(email):
    url = "https://services.leadconnectorhq.com/contacts/"
    payload = {
        "email": email,
        "firstName": "Owner",
        "lastName": "Admin",
        "name": "Owner Admin",
        "locationId": GHL_LOC,
        "tags": ["admin", "system-owner"]
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code in [200, 201]:
         cid = r.json()['contact']['id']
         print(f"✅ Created Owner: {cid}")
         return cid
    else:
        print(f"❌ Failed to create: {r.text}")

if __name__ == "__main__":
    check_owner()
