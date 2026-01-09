# debug_ghl_sms.py
import requests
import os
import json
from dotenv import load_dotenv

# Force reload of env vars
load_dotenv(override=True)

TOKEN = os.getenv("GHL_AGENCY_API_TOKEN")
LOCATION_ID = "RnK4OjX0oDcqtWw00VyLr" 
TARGET_PHONE = "+13527585336"

print(f"Using Token: {TOKEN[:0]}... (Hidden)")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def create_contact():
    url = "https://services.leadconnectorhq.com/contacts/"
    payload = {
        "locationId": LOCATION_ID,
        "phone": TARGET_PHONE,
        "firstName": "Boss",
        "lastName": "User",
        "tags": ["john-demo"]
    }
    print(f"Creating Contact: {url}")
    res = requests.post(url, headers=headers, json=payload)
    print(f"Create Status: {res.status_code}")
    print(res.text)
    if res.status_code in [200, 201]:
        return res.json().get('contact', {}).get('id')
    return None

def send_sms(contact_id):
    url = "https://services.leadconnectorhq.com/conversations/messages"
    payload = {
        "type": "SMS",
        "contactId": contact_id,
        "message": "John here. Trying you again. Let me know if you get this.",
        "subject": "John Demo"
    }
    print(f"Sending SMS: {url}")
    res = requests.post(url, headers=headers, json=payload)
    print(f"Send Status: {res.status_code}")
    print(res.text)

# 1. Search first
print("Searching for contact...")
search_url = "https://services.leadconnectorhq.com/contacts/search"
res = requests.post(search_url, headers=headers, json={"locationId": LOCATION_ID, "query": TARGET_PHONE})
contact_id = None

if res.status_code == 200:
    data = res.json()
    contacts = data.get('contacts', [])
    if contacts:
        contact_id = contacts[0]['id']
        print(f"Found Contact: {contact_id}")
    else:
        print("Contact not found in search.")
else:
    print(f"Search Failed: {res.status_code} {res.text}")

# 2. Create if missing
if not contact_id:
    contact_id = create_contact()

# 3. Send
if contact_id:
    send_sms(contact_id)
else:
    print("Could not get Contact ID.")
