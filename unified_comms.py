"""
Unified Communication System
============================
GHL-first, Resend-fallback architecture.
All messages go through GHL so Sarah can monitor conversations.
If GHL fails, falls back to Resend and logs for manual GHL entry.

ARCHITECTURE:
1. Try GHL email/SMS first (Sarah can see full conversation)
2. If GHL fails (401, timeout), use Resend/Twilio as backup
3. Log all messages to Supabase for tracking
"""
import os
import requests
import resend
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Config
GHL_API_KEY = os.getenv('GHL_API_TOKEN')
GHL_LOCATION_ID = os.getenv('GHL_LOCATION_ID')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
resend.api_key = RESEND_API_KEY

GHL_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json"
}

def send_email(to_email: str, subject: str, body: str, contact_id: str = None) -> dict:
    """
    Send email via GHL first, fallback to Resend.
    Returns: {"provider": "ghl"|"resend", "success": bool, "details": ...}
    """
    result = {"timestamp": datetime.now().isoformat(), "to": to_email, "subject": subject}
    
    # TRY GHL FIRST
    if contact_id:
        try:
            ghl_url = "https://services.leadconnectorhq.com/conversations/messages"
            ghl_payload = {
                "type": "Email",
                "contactId": contact_id,
                "subject": subject,
                "html": body
            }
            ghl_resp = requests.post(ghl_url, headers=GHL_HEADERS, json=ghl_payload, timeout=10)
            
            if ghl_resp.status_code in [200, 201]:
                result["provider"] = "ghl"
                result["success"] = True
                result["message_id"] = ghl_resp.json().get("messageId")
                print(f"✅ Email sent via GHL: {to_email}")
                return result
            else:
                print(f"⚠️ GHL failed ({ghl_resp.status_code}), trying Resend...")
        except Exception as e:
            print(f"⚠️ GHL error: {e}, trying Resend...")
    
    # FALLBACK TO RESEND
    try:
        resend_resp = resend.Emails.send({
            "from": "Daniel <daniel@aiserviceco.com>",
            "to": [to_email],
            "reply_to": "owner@aiserviceco.com",
            "subject": subject,
            "html": body
        })
        result["provider"] = "resend"
        result["success"] = True
        result["message_id"] = resend_resp.get("id")
        result["note"] = "Sent via Resend - add to GHL manually if needed"
        print(f"✅ Email sent via Resend (backup): {to_email}")
        return result
    except Exception as e:
        result["provider"] = "failed"
        result["success"] = False
        result["error"] = str(e)
        print(f"❌ Both GHL and Resend failed: {e}")
        return result


def send_sms(to_phone: str, message: str, contact_id: str = None) -> dict:
    """
    Send SMS via GHL first, fallback to Twilio.
    """
    result = {"timestamp": datetime.now().isoformat(), "to": to_phone}
    
    # TRY GHL FIRST
    if contact_id:
        try:
            ghl_url = "https://services.leadconnectorhq.com/conversations/messages"
            ghl_payload = {
                "type": "SMS",
                "contactId": contact_id,
                "message": message
            }
            ghl_resp = requests.post(ghl_url, headers=GHL_HEADERS, json=ghl_payload, timeout=10)
            
            if ghl_resp.status_code in [200, 201]:
                result["provider"] = "ghl"
                result["success"] = True
                print(f"✅ SMS sent via GHL: {to_phone}")
                return result
            else:
                print(f"⚠️ GHL SMS failed ({ghl_resp.status_code})")
        except Exception as e:
            print(f"⚠️ GHL SMS error: {e}")
    
    # FALLBACK TO TWILIO
    try:
        from twilio.rest import Client
        client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        msg = client.messages.create(
            body=message,
            from_=os.getenv('TWILIO_FROM_NUMBER'),
            to=to_phone
        )
        result["provider"] = "twilio"
        result["success"] = True
        result["sid"] = msg.sid
        result["note"] = "Sent via Twilio - may have delivery issues, add to GHL manually"
        print(f"✅ SMS sent via Twilio (backup): {to_phone}")
        return result
    except Exception as e:
        result["provider"] = "failed"
        result["success"] = False
        result["error"] = str(e)
        print(f"❌ Both GHL and Twilio failed: {e}")
        return result


def find_or_create_ghl_contact(email: str = None, phone: str = None, name: str = None) -> str:
    """Find existing GHL contact or create new one. Returns contact_id."""
    if email:
        lookup_url = f"https://services.leadconnectorhq.com/contacts/lookup?email={email}&locationId={GHL_LOCATION_ID}"
    elif phone:
        lookup_url = f"https://services.leadconnectorhq.com/contacts/lookup?phone={phone}&locationId={GHL_LOCATION_ID}"
    else:
        return None
    
    try:
        resp = requests.get(lookup_url, headers=GHL_HEADERS, timeout=10)
        if resp.status_code == 200 and resp.json().get('contacts'):
            return resp.json()['contacts'][0]['id']
        
        # Create new contact
        create_resp = requests.post(
            "https://services.leadconnectorhq.com/contacts/",
            headers=GHL_HEADERS,
            json={
                "email": email,
                "phone": phone,
                "name": name or "Prospect",
                "locationId": GHL_LOCATION_ID
            },
            timeout=10
        )
        if create_resp.status_code in [200, 201]:
            return create_resp.json().get('contact', {}).get('id')
    except Exception as e:
        print(f"⚠️ GHL contact lookup failed: {e}")
    
    return None


if __name__ == "__main__":
    # Test the system
    TEST_EMAIL = "seaofwith@gmail.com"
    TEST_PHONE = os.getenv('TEST_PHONE')
    
    print("=== Testing Unified Comms ===")
    print("\n1. Testing Email...")
    email_result = send_email(
        TEST_EMAIL,
        "Test: Unified Comms System",
        "<p>Hey! This is a test of the unified comms system. GHL-first, Resend-backup.</p>"
    )
    print(f"   Result: {email_result}")
    
    print("\n2. Testing SMS...")
    sms_result = send_sms(TEST_PHONE, "Test from unified comms system!")
    print(f"   Result: {sms_result}")
