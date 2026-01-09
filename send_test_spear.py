import os
import requests
import json
import re
from dotenv import load_dotenv

# Load Env
load_dotenv(".env")

TEST_TARGET_EMAIL = "seaofdiscipline@gmail.com"

# Content from SPEAR_BATCH_REVIEW.md (Target 1)
EMAIL_SUBJECT = "Quick question for Cooling 21"
EMAIL_BODY_MD = """
Hi Owner 21,

I noticed your missed call automation could be improved. I'm building a custom ROI breakdown for Cooling 21 here:

<a href="https://aiserviceco.com/audit/cooling21">Link to Custom Audit</a>

Book a Call: <a href="https://www.aiserviceco.com/features.html">https://www.aiserviceco.com/features.html</a>

If you want to fix this bottleneck, let's chat.

Fellow Spartan Daniel , Learn Evolve and Grow Always!!
"""

def send_test_outreach():
    print(f"📧 IO: Sending TEST Spear Campaign Email to {TEST_TARGET_EMAIL}...")
    
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

    # 1. Find or Create Contact for Test Target
    contact_id = None
    print(f"✨ Creating/Upserting Test Contact ({TEST_TARGET_EMAIL})...")
    create_url = "https://services.leadconnectorhq.com/contacts/"
    create_payload = {
        "email": TEST_TARGET_EMAIL,
        "firstName": "Test",
        "lastName": "Target",
        "locationId": loc_id,
        "tags": ["test-segment", "spear-test"],
        "dnd": False
    }
    
    try:
        res = requests.post(create_url, json=create_payload, headers=headers)
        if res.status_code in [200, 201]:
            contact_id = res.json()['contact']['id']
            print(f"✅ Created Test Contact: {contact_id}")
        elif res.status_code == 400:
            # Try to grab ID from 400 error if duplicate
            try:
                err_json = res.json()
                contact_id = err_json.get('meta', {}).get('contactId') or err_json.get('contact', {}).get('id')
                if contact_id:
                     print(f"✅ Recovered Test ID from Duplicate: {contact_id}")
                else:
                    # Fallback Regex
                    match = re.search(r'"id"\s*:\s*"([^"]+)"', res.text)
                    if match:
                        contact_id = match.group(1)
                        print(f"✅ Recovered Test ID (Regex): {contact_id}")
            except:
                pass
                
        if not contact_id:
            print(f"❌ Could not resolve Contact ID. Resp: {res.text}")
            return

    except Exception as e:
        print(f"❌ Creation Ex: {e}")
        return

    # 3. Send Real Email
    print(f"🚀 Dispatching SPEAR Email (ID: {contact_id})...")
    send_url = "https://services.leadconnectorhq.com/conversations/messages"
    
    email_payload = {
        "type": "Email",
        "contactId": contact_id,
        "locationId": loc_id,
        "emailFrom": "system@aiserviceco.com",
        "emailSubject": EMAIL_SUBJECT,
        "html": EMAIL_BODY_MD.replace("\n", "<br>") # Simple HTML formatting
    }
    
    try:
        res = requests.post(send_url, json=email_payload, headers=headers)
        if res.status_code in [200, 201]:
            print("✅ TEST EMAIL SENT SUCCESSFULLY.")
            print(f"Response: {res.json()}")
        else:
            print(f"❌ Email Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Dispatch Error: {e}")

if __name__ == "__main__":
    send_test_outreach()
