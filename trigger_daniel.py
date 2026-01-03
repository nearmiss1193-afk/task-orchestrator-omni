
import os
import requests
import json
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

GHL_token = os.environ.get("GHL_API_TOKEN")
GHL_LOC = os.environ.get("GHL_LOCATION_ID")

TARGET_EMAIL = "danielcoffman@businessconector.com"
TARGET_NAME = "Daniel Coffman"
OFFER_LINK = "https://nearmiss1193-afk--ghl-omni-automation-hvac-landing.modal.run"

def get_headers():
    return {
        "Authorization": f"Bearer {GHL_token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }

def find_contact(email):
    url = f"https://services.leadconnectorhq.com/contacts/search/duplicate?locationId={GHL_LOC}&email={email}"
    res = requests.get(url, headers=get_headers())
    if res.status_code == 200:
        data = res.json()
        if data.get("contact"):
            return data.get("contact").get("id")
    return None

def create_contact(email, name):
    url = "https://services.leadconnectorhq.com/contacts/"
    payload = {
        "email": email,
        "name": name,
        "firstName": name.split(" ")[0],
        "lastName": name.split(" ")[1] if " " in name else "",
        "locationId": GHL_LOC,
        "tags": ["secret-shopper", "hvac-offer-test"]
    }
    res = requests.post(url, json=payload, headers=get_headers())
    if res.status_code in [200, 201]:
        return res.json().get("contact", {}).get("id")
    print(f"❌ Failed to create contact: {res.text}")
    return None

def send_email(contact_id, email, link):
    url = "https://services.leadconnectorhq.com/conversations/messages"
    
    # Needs a conversation ID? Or can init via messages/email?
    # GHL API allows creating an outbound message without existing conversation if we provide contactId
    # Actually, we should use the 'email' type.
    
    payload = {
        "type": "Email",
        "contactId": contact_id,
        "emailFrom": "owner@aiserviceco.com", # Sender (Make sure this exists in GHL SMTP or defaults)
        "emailTo": email,
        "subject": "Here is the HVAC AI Offer (Secret Shop)",
        "html": f"""
        <p>Hi Daniel,</p>
        <p>This is the secret shop test link for the HVAC AI System.</p>
        <p><strong>Offer Link:</strong> <a href="{link}">{link}</a></p>
        <p>Please test the funnel and let us know your feedback.</p>
        <p>Best,<br>AI Service Co (Automated)</p>
        """
    }
    
    # Note: emailFrom might require verification. If it fails, try without it (default SMTP).
    
    res = requests.post(url, json=payload, headers=get_headers())
    if res.status_code in [200, 201]:
        print("✅ Email Sent Successfully to Daniel.")
        return True
    else:
        print(f"❌ Failed to send email: {res.text}")
        return False

print("🚀 Initiating Secret Shop Trigger for Daniel...")

cid = find_contact(TARGET_EMAIL)
if not cid:
    print("New contact...")
    cid = create_contact(TARGET_EMAIL, TARGET_NAME)
else:
    print(f"Found existing contact: {cid}")

if cid:
    send_email(cid, TARGET_EMAIL, OFFER_LINK)
else:
    print("Could not get Contact ID. Aborting.")
