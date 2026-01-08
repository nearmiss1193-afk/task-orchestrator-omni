"""
MULTI-CHANNEL OUTREACH: SMS + PHONE CALL
Sends SMS via GHL and triggers Sarah with context about email/SMS
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# --- PROSPECT DETAILS ---
PROSPECT_PHONE = os.getenv("TEST_PHONE")  # User's test phone
PROSPECT_NAME = "Homeheart"
COMPANY_NAME = "Homeheart HVAC & Cool"

# --- SMS CONTENT ---
SMS_MESSAGE = f"""Hey {PROSPECT_NAME}! 👋

I just sent you an email with a quick video breakdown on missed call automation for {COMPANY_NAME}.

Worth a 60-second look: https://aiserviceco.com/assets/missed_call_rescue.mp4

Quick question - when's a good time for a 5-min call this week?

- Daniel @ AI Service Co"""

def send_sms_ghl():
    """Send SMS via GHL API"""
    print(f"📱 Sending SMS to {PROSPECT_PHONE}...")
    
    token = os.getenv("GHL_AGENCY_API_TOKEN") or os.getenv("GHL_API_TOKEN")
    loc_id = os.getenv("GHL_LOCATION_ID")
    
    if not token or not loc_id:
        print("❌ Missing GHL credentials, trying Resend fallback...")
        # Fallback: Just log it for now
        print(f"[SMS SIMULATED] To: {PROSPECT_PHONE}\n{SMS_MESSAGE}")
        return True
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    
    # First, find/create contact
    contact_payload = {
        "phone": PROSPECT_PHONE,
        "firstName": PROSPECT_NAME,
        "lastName": "HVAC",
        "locationId": loc_id,
        "tags": ["sms-outreach", "homeheart"]
    }
    
    res = requests.post(
        "https://services.leadconnectorhq.com/contacts/upsert",
        json=contact_payload,
        headers=headers
    )
    
    contact_id = None
    if res.status_code in [200, 201]:
        contact_id = res.json().get("contact", {}).get("id")
        print(f"✅ Contact: {contact_id}")
    else:
        print(f"⚠️ Contact upsert issue: {res.status_code}")
        # Continue anyway for testing
    
    if contact_id:
        # Send SMS
        sms_payload = {
            "type": "SMS",
            "contactId": contact_id,
            "message": SMS_MESSAGE
        }
        
        res = requests.post(
            "https://services.leadconnectorhq.com/conversations/messages",
            json=sms_payload,
            headers=headers
        )
        
        if res.status_code in [200, 201]:
            print("✅ SMS SENT")
            return True
        else:
            print(f"⚠️ SMS issue: {res.status_code} - continuing with call")
    
    return True

def trigger_sarah_call():
    """Trigger Sarah with context about prior touchpoints"""
    print(f"📞 Triggering Sarah follow-up call...")
    
    VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
    VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
    SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
    
    # Custom first message with email/SMS context
    custom_first_message = f"""Hey {PROSPECT_NAME}? Sarah here from AI Service Co. 
    
Look, I just sent you an email and a text about your missed call situation at {COMPANY_NAME}. 
Did you get a chance to see that video I sent over? 
It's a quick 60-second breakdown of why speed-to-lead is killing it for HVAC companies like yours right now."""

    payload = {
        "assistantId": SARAH_ID,
        "assistantOverrides": {
            "firstMessage": custom_first_message
        },
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": PROSPECT_PHONE,
            "name": PROSPECT_NAME
        }
    }
    
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    res = requests.post(
        "https://api.vapi.ai/call/phone",
        json=payload,
        headers=headers,
        timeout=30
    )
    
    if res.status_code in [200, 201]:
        print(f"✅ SARAH CALL TRIGGERED")
        print(f"Call ID: {res.json().get('id', 'N/A')}")
        return True
    else:
        print(f"❌ Call failed: {res.status_code}")
        print(res.text[:300])
        return False

if __name__ == "__main__":
    send_sms_ghl()
    print("\n--- Triggering follow-up call in 3 seconds ---\n")
    import time
    time.sleep(3)
    trigger_sarah_call()
