import os
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

GHL_TOKEN = os.environ.get("GHL_API_TOKEN")
GHL_LOCATION = os.environ.get("GHL_LOCATION_ID")
OWNER_EMAIL = "owner@aiserviceco.com"
OWNER_PHONE = "+13529368152"

HEADERS = {
    'Authorization': f'Bearer {GHL_TOKEN}',
    'Version': '2021-07-28',
    'Content-Type': 'application/json'
}

OWNER_CONTACT_ID = "2uuVuOP0772z7hay16og"

def send_ghl_notification(subject, body_html, type="Email"):
    """
    Sends a real notification message to the owner via GHL Conversations.
    """
    url = f"https://services.leadconnectorhq.com/conversations/messages"
    payload = {
        "type": type,
        "contactId": OWNER_CONTACT_ID,
        "emailFrom": "system@aiserviceco.com",
        "emailSubject": subject,
        "html": body_html if type == "Email" else None,
        "message": body_html if type == "SMS" else None
    }
    
    try:
        r = requests.post(url, json=payload, headers=HEADERS)
        print(f"[{type}] Notification Status: {r.status_code}")
        return r.json()
    except Exception as e:
        print(f"[{type}] Notification Error: {e}")
        return None

if __name__ == "__main__":
    # Test Email
    test_email = f"<h1>Spartan System Live</h1><p>Real-time notifications are now active. All outreach will be CC'd here.</p>"
    send_ghl_notification("[LIVE] Spartan Priority Notification", test_email, type="Email")
    
    # Test SMS
    test_sms = "Spartan System: Real-time SMS alerts are now active for all lead responses."
    send_ghl_notification(None, test_sms, type="SMS")
