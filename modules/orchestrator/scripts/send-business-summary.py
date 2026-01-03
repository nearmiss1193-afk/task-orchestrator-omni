import os
from dotenv import load_dotenv
import requests

load_dotenv(".env.local")

OWNER_EMAIL = os.environ.get("GHL_EMAIL") or "nearmiss1193@gmail.com"
REPORT_PATH = "C:\\Users\\nearm\\.gemini\\antigravity\\brain\\d91de16e-14b7-4513-a02b-aee6e62b91d0\\autonomous_business_capabilities.md"

def send_summary():
    print(f"--- DISPATCHING BUSINESS CAPABILITIES REPORT ---")
    
    if not os.path.exists(REPORT_PATH):
        print(f"Error: Report not found at {REPORT_PATH}")
        return

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"To: {OWNER_EMAIL}")
    print(f"Subject: [INTELLIGENCE] Autonomous Business Capabilities Framework")
    
    # Actually Send via GHL API
    ghl_token = os.environ.get("GHL_PRIVATE_KEY")
    location_id = os.environ.get("GHL_LOCATION_ID")
    
    if ghl_token and location_id:
        try:
            # 1. Resolve Contact (Simple search by email)
            headers = {"Authorization": f"Bearer {ghl_token}", "Version": "2021-04-15", "Content-Type": "application/json"}
            search_url = f"https://services.leadconnectorhq.com/contacts/search?query={OWNER_EMAIL}&locationId={location_id}"
            s_res = requests.get(search_url, headers=headers)
            contact_id = s_res.json().get('contacts', [{}])[0].get('id')
            
            if contact_id:
                dispatch_url = "https://services.leadconnectorhq.com/conversations/messages"
                payload = {
                    "type": "Email",
                    "contactId": contact_id,
                    "subject": "[INTELLIGENCE] Autonomous Business Capabilities Framework",
                    "html": f"<h3>Capability Audit</h3><pre>{content}</pre>",
                    "body": content
                }
                requests.post(dispatch_url, json=payload, headers=headers)
                print(f"✅ REPORT DISPATCHED TO {OWNER_EMAIL} via GHL API")
            else:
                print(f"⚠️ Could not find contact in GHL for {OWNER_EMAIL}")
        except Exception as e:
            print(f"❌ Error sending via GHL: {str(e)}")
    else:
        print(f"⚠️ Missing GHL configuration for real dispatch.")

if __name__ == "__main__":
    send_summary()
