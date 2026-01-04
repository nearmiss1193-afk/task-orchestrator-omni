
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

    def send_sms(self, to_phone, body):
        """Sends SMS via Twilio."""
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
            print(f"✅ SMS SENT to {to_phone}. SID: {msg.sid}")
            return True
        except Exception as e:
            print(f"❌ SMS Failed: {e}")
            return False

# Singleton instance for easy import
dispatcher = SovereignDispatch()
