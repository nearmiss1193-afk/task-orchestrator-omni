
import os
import requests
from twilio.rest import Client
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

class SovereignDispatch:
    def __init__(self):
        self.resend_key = os.environ.get("RESEND_API_KEY", "").strip()
        self.twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
        self.twilio_token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
        self.twilio_from = os.environ.get("TWILIO_FROM_NUMBER", "").strip()
        
        # GHL Config
        self.ghl_token = os.environ.get("GHL_API_TOKEN", "").strip()
        self.ghl_location = os.environ.get("GHL_LOCATION_ID", "").strip()
        
        if not self.resend_key:
            print("⚠️ SovereignDispatch: RESEND_API_KEY missing. Emails will fail.")
        
        if not (self.twilio_sid and self.twilio_token):
             print("⚠️ SovereignDispatch: Twilio Credentials missing. SMS will be skipped.")

    def send_email(self, to_email, subject, html_body):
        """Sends an email via Resend."""
        if not self.resend_key:
            print("❌ Email Blocked: No Key")
            return False

        headers = {
            'Authorization': f'Bearer {self.resend_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "from": "Sovereign AI <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_body
        }
        
        try:
            res = requests.post("https://api.resend.com/emails", json=payload, headers=headers)
            if res.status_code in [200, 201]:
                print(f"✅ EMAIL SENT to {to_email}. ID: {res.json().get('id')}")
                return True
            else:
                print(f"❌ Email API Error: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            print(f"❌ Email Exception: {e}")
            return False

    def send_sms(self, to_phone, body, provider="twilio"):
        """Sends SMS via Twilio or GHL."""
        
        # GHL OVERRIDE
        if provider == "ghl":
            return self.send_ghl_sms(to_phone, body)

        if not (self.twilio_sid and self.twilio_token and self.twilio_from):
            print("⏭️ SMS Skipped (No Config)")
            return False

        try:
            client = Client(self.twilio_sid, self.twilio_token)
            msg = client.messages.create(
                body=body,
                from_=self.twilio_from,
                to=to_phone
            )
            print(f"✅ TWILIO SMS SENT to {to_phone}. SID: {msg.sid}")
            return True
        except Exception as e:
            print(f"❌ SMS Failed: {e}")
            return False

    def send_ghl_sms(self, to_phone, body):
        """Sends SMS via GoHighLevel API conversation."""
        if not (self.ghl_token and self.ghl_location):
            print("❌ GHL SMS Failed: Missing Credentials")
            return False

        url = "https://services.leadconnectorhq.com/conversations/messages"
        headers = {
            "Authorization": f"Bearer {self.ghl_token}",
            "Version": "2021-04-15",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 1. Lookup Contact to get ID (Required for GHL SMS usually, or can send to 'to' directly if supported)
        # GHL V2 API usually requires a 'contactId' or creating a conversation.
        # Shortcuts: sending a 'message' type 'SMS' to a phone number.
        
        payload = {
            "type": "SMS",
            "to": to_phone,
            "message": body
        }
        # Note: Depending on specific GHL API version (1.0 vs 2.0), this might need adjustment.
        # Fallback to creating a contact if direct send fails? No, let's try direct conversation message.
        
        try:
            res = requests.post(url, json=payload, headers=headers)
            if res.status_code in [200, 201]:
                 print(f"✅ GHL SMS SENT to {to_phone}.")
                 return True
            else:
                 print(f"❌ GHL SMS API Error: {res.status_code} - {res.text}")
                 return False
        except Exception as e:
            print(f"❌ GHL SMS Exception: {e}")
            return False

# Singleton instance for easy import
dispatcher = SovereignDispatch()
