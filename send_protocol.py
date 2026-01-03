import os
import requests
import json
import re
from dotenv import load_dotenv

# Load Env
load_dotenv(".env")

OWNER_EMAIL = "owner@aiserviceco.com"
SUBJECT = "🚨 SYSTEM RECOVERY PROTOCOL (2025-12-31)"

def send_protocol():
    print(f"📧 IO: Real Email Dispatch to {OWNER_EMAIL}...")
    
    token = os.environ.get("GHL_AGENCY_API_TOKEN") or os.environ.get("GHL_API_TOKEN")
    loc_id = os.environ.get("GHL_LOCATION_ID")
    
    if not token or not loc_id:
        print("❌ Error: Missing GHL Credentials in .env")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Location-Id": loc_id
    }

    # 1. Read Protocol
    try:
        with open(r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400\RECOVERY_PROTOCOL.md", "r", encoding="utf-8") as f:
            protocol_content = f.read()
    except FileNotFoundError:
        print("❌ Protocol Artifact not found!")
        return

    # 2. Find or Create Contact
    contact_id = None
    
    # Attempt 2: Create if not found (Skipping search to force flow)
    print("✨ Creating/Upserting New Owner Contact...")
    create_url = "https://services.leadconnectorhq.com/contacts/"
    create_payload = {
        "email": OWNER_EMAIL,
        "firstName": "System",
        "lastName": "Owner",
        "locationId": loc_id,
        "tags": ["admin", "system-owner"],
        "dnd": False
    }
    try:
        res = requests.post(create_url, json=create_payload, headers=headers)
        if res.status_code in [200, 201]:
            contact_id = res.json()['contact']['id']
            print(f"✅ Created Owner: {contact_id}")
        elif res.status_code == 400:
            # REGEX EXTRACTION from raw text
            match = re.search(r'"id":"([a-zA-Z0-9-]+)"', res.text)
            if match:
                contact_id = match.group(1)
                print(f"✅ Recovered Owner ID (Regex): {contact_id}")
            else:
                print(f"❌ 400 Error (Regex Failed): {res.text}")
                # Try search fallback
                # ... skipping for brevity
                return
        else:
            print(f"❌ Creation Failed: {res.text}")
            return
    except Exception as e:
        print(f"❌ Creation Ex: {e}")
        return

    if not contact_id:
        print("❌ No Contact ID found.")
        return

    # 3. Send Real Email
    print(f"🚀 Dispatching Protocol via GHL Email (ID: {contact_id})...")
    send_url = "https://services.leadconnectorhq.com/conversations/messages"
    
    html_body = f"<h2>⚠️ SYSTEM RECOVERY PROTOCOL</h2><p>Attached/Below is the latest recovery manifest.</p><hr/><pre>{protocol_content}</pre>"
    
    email_payload = {
        "type": "Email",
        "contactId": contact_id,
        "locationId": loc_id, # Added this just in case
        "emailFrom": "system@aiserviceco.com",
        "emailSubject": SUBJECT,
        "html": html_body
    }
    
    try:
        res = requests.post(send_url, json=email_payload, headers=headers)
        if res.status_code in [200, 201]:
            print("✅ REAL EMAIL SENT SUCCESSFULLY.")
            print(f"Response: {res.json()}")
        else:
            print(f"❌ Email Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Dispatch Error: {e}")

if __name__ == "__main__":
    send_protocol()
