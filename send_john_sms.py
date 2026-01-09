# send_john_sms.py - Send SMS from "John"
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GHL_AGENCY_API_TOKEN")
LOCATION_ID = "RnK4OjX0oDcqtWw00VyLr" # AI Service Company
YOUR_NUMBER = "+13527585336"

url = "https://services.leadconnectorhq.com/conversations/messages"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# 1. First, we need to find the Contact ID for your number
print("Finding contact...")
search_url = "https://services.leadconnectorhq.com/contacts/search"
search_payload = {
    "locationId": LOCATION_ID,
    "query": YOUR_NUMBER
}
contact_id = None
try:
    s_res = requests.post(search_url, headers=headers, json=search_payload)
    if s_res.status_code == 200:
        contacts = s_res.json().get('contacts', [])
        if contacts:
            contact_id = contacts[0].get('id')
            print(f"Found Contact ID: {contact_id}")
    else:
        print(f"Search failed: {s_res.text}")
except Exception as e:
    print(f"Search Error: {e}")

# If no contact, create one (skip for now, assume exist from call)
if not contact_id:
    print("Contact not found. Sending to number directly (may require contact creation).")
    # GHL often requires a contactId for conversation messages, but let's try direct SMS endpoint if available or create contact
    # Creating contact
    print("Creating contact...")
    create_url = "https://services.leadconnectorhq.com/contacts/"
    create_payload = {
        "locationId": LOCATION_ID,
        "phone": YOUR_NUMBER,
        "firstName": "Boss",
        "lastName": "User"
    }
    c_res = requests.post(create_url, headers=headers, json=create_payload)
    if c_res.status_code in [200, 201]:
        contact_id = c_res.json().get('contact', {}).get('id')
        print(f"Created Contact ID: {contact_id}")

if contact_id:
    print("Sending SMS...")
    payload = {
        "type": "SMS",
        "contactId": contact_id,
        "message": "Hey, it's John from the roofing team. Just tried calling you. When's a good time to chat about those leads?",
        "subject": "Roofing Leads"
    }
    
    res = requests.post(url, headers=headers, json=payload)
    
    if res.status_code in [200, 201]:
        print("\n[SUCCESS] SMS Sent!")
        print(res.json())
    else:
        print(f"\n[ERROR] {res.status_code}")
        print(res.text)
else:
    print("Could not get Contact ID. Aborting SMS.")
