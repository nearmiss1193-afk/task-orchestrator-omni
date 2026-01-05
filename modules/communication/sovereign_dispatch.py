
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
        self.vapi_key = os.environ.get("VAPI_PRIVATE_KEY", "").strip()
        self.vapi_assistant_id = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah the Spartan
        
        # GHL Config
        self.ghl_token = os.environ.get("GHL_API_TOKEN", "").strip()
        self.ghl_location = os.environ.get("GHL_LOCATION_ID", "").strip()
        
        print(f"[INFO] GHL Token Loaded: {'YES' if self.ghl_token else 'NO'} ({self.ghl_token[:4]}...)")
        print(f"[INFO] GHL Location Loaded: {'YES' if self.ghl_location else 'NO'} ({self.ghl_location})")
        
        if not self.resend_key:
            print("[WARN] SovereignDispatch: RESEND_API_KEY missing. Emails will fail.")
        
        if not (self.twilio_sid and self.twilio_token):
             print("⚠️ SovereignDispatch: Twilio Credentials missing. SMS will be skipped.")

    def send_email(self, to_email, subject, html_body, provider="resend"):
        """Sends an email via Resend or GHL."""
        
        # GHL OVERRIDE
        if provider == "ghl":
            sent = self.send_ghl_email(to_email, subject, html_body)
            if sent:
                return True
            print("[WARN] GHL Email Failed. Falling back to Resend...")
            # Fall through to Resend logic below

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
                print(f"[OK] EMAIL SENT to {to_email}. ID: {res.json().get('id')}")
                return True
            else:
                print(f"[ERR] Email API Error: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            print(f"[ERR] Email Exception: {e}")
            return False

    def send_sms(self, to_phone, body, provider="twilio"):
        """Sends SMS via Twilio or GHL."""
        
        # GHL OVERRIDE
        if provider == "ghl":
            return self.send_ghl_sms(to_phone, body)

        if not (self.twilio_sid and self.twilio_token and self.twilio_from):
            print("[SKIP] SMS Skipped (No Config)")
            return False

        try:
            client = Client(self.twilio_sid, self.twilio_token)
            msg = client.messages.create(
                body=body,
                from_=self.twilio_from,
                to=to_phone
            )
            print(f"[OK] TWILIO SMS SENT to {to_phone}. SID: {msg.sid}")
            return True
        except Exception as e:
            print(f"[ERR] SMS Failed: {e}")
            return False

    def make_call(self, to_phone, assistant_id=None):
        """Initiates an outbound Vapi call."""
        if not self.vapi_key:
            print("❌ Call Blocked: No Vapi Key")
            return False

        target_assistant = assistant_id or self.vapi_assistant_id
        
        headers = {
            'Authorization': f'Bearer {self.vapi_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "phoneNumberId": "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e",  # From Vapi Dashboard Screenshot
            "customer": {
                "number": to_phone,
                "name": "Commander"
            },
            "assistantId": target_assistant
        }

        try:
            print(f"[INFO] Dialing {to_phone} via Vapi...")
            res = requests.post("https://api.vapi.ai/call/phone", json=payload, headers=headers)
            if res.status_code in [200, 201]:
                call_id = res.json().get('id', 'Unknown')
                print(f"[OK] CALL INITIATED. ID: {call_id}")
                return True
            else:
                print(f"[ERR] Call API Error: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            print(f"[ERR] Call Exception: {e}")
            return False

    # --- GHL HELPER METHODS ---
    def _ghl_request(self, method, endpoint, payload=None, params=None):
        """Helper for GHL API requests."""
        url = f"https://services.leadconnectorhq.com/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.ghl_token}",
            "Version": "2021-07-28", # Updated to a newer stable version
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        try:
            print(f"[DEBUG] GHL {method} -> {url}")
            if method == "GET":
                res = requests.get(url, headers=headers, params=params)
            else:
                res = requests.post(url, json=payload, headers=headers)
            
            print(f"      Code: {res.status_code}")
            if res.status_code not in [200, 201]:
                print(f"      ERR: {res.text}")
            return res
        except Exception as e:
            print(f"[ERR] GHL Request Error: {e}")
            return None

    def _get_or_create_contact(self, phone=None, email=None, name="Sovereign Lead"):
        """Resolves a Contact ID from Phone or Email, creating if necessary."""
        
        # 1. Try Lookup by Phone
        if phone:
            params = {"query": phone, "locationId": self.ghl_location}
            res = self._ghl_request("GET", "contacts/", params=params)
            if res:
                 if res.status_code == 200:
                    data = res.json()
                    if data.get('contacts') and len(data['contacts']) > 0:
                        cid = data['contacts'][0]['id']
                        print(f"   [OK] GHL Lookup Hit (Phone): {cid}")
                        return cid
                 else:
                    print(f"   [MISS] GHL Lookup Miss (Phone) {res.status_code}: {res.text}")

        # 2. Try Lookup by Email
        if email:
            params = {"query": email, "locationId": self.ghl_location}
            res = self._ghl_request("GET", "contacts/", params=params)
            if res:
                if res.status_code == 200:
                    data = res.json()
                    if data.get('contacts') and len(data['contacts']) > 0:
                        cid = data['contacts'][0]['id']
                        print(f"   [OK] GHL Lookup Hit (Email): {cid}")
                        return cid
                else:
                    print(f"   [MISS] GHL Lookup Miss (Email) {res.status_code}: {res.text}")

        # 3. Create New Contact
        print(f"[INFO] Contact not found. Creating: {name}")
        payload = {
            "firstName": name.split(" ")[0],
            "lastName": " ".join(name.split(" ")[1:]) if " " in name else "",
            "name": name,
            "locationId": self.ghl_location,
            "phone": phone,
            "email": email
        }
        # Clean nulls
        payload = {k: v for k, v in payload.items() if v}
        
        res = self._ghl_request("POST", "contacts/", payload=payload)
        if res and res.status_code in [200, 201]:
            return res.json().get('contact', {}).get('id')
        else:
             if res: print(f"[ERR] Contact Creation Failed: {res.text}")
             return None

    def send_ghl_email(self, to_email, subject, html_body):
        """Sends Email via GoHighLevel API conversation."""
        if not (self.ghl_token and self.ghl_location):
            print("[ERR] GHL Email Failed: Missing Credentials")
            return False

        # Resolve Contact
        contact_id = self._get_or_create_contact(email=to_email, name="Sovereign User")
        if not contact_id:
            print("[ERR] GHL Email Failed: Could not resolve Contact ID.")
            return False

        payload = {
            "type": "Email",
            "contactId": contact_id,
            "email": to_email,
            "subject": subject,
            "html": html_body
        }
        
        res = self._ghl_request("POST", "conversations/messages", payload=payload)
        if res and res.status_code in [200, 201]:
             print(f"[OK] GHL EMAIL SENT to {to_email}.")
             return True
        else:
             if res: print(f"[ERR] GHL Email API Error: {res.status_code} - {res.text}")
             return False

    def send_ghl_sms(self, to_phone, body):
        """Sends SMS via GoHighLevel API conversation."""
        if not (self.ghl_token and self.ghl_location):
            print("[ERR] GHL SMS Failed: Missing Credentials")
            return False

        # Resolve Contact
        contact_id = self._get_or_create_contact(phone=to_phone, name="Sovereign User")
        if not contact_id:
             print("[ERR] GHL SMS Failed: Could not resolve Contact ID.")
             return False
        
        payload = {
            "type": "SMS",
            "contactId": contact_id,
            "to": to_phone,
            "message": body
        }
        
        res = self._ghl_request("POST", "conversations/messages", payload=payload)
        if res and res.status_code in [200, 201]:
             print(f"[OK] GHL SMS SENT to {to_phone}.")
             return True
        else:
             if res: print(f"[ERR] GHL SMS API Error: {res.status_code} - {res.text}")
             return False

    def get_conversation_messages(self, conversation_id):
        """Fetches message history for a conversation."""
        url = f"https://services.leadconnectorhq.com/conversations/{conversation_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.ghl_token}",
            "Version": "2021-07-28",
            "Accept": "application/json"
        }
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                return res.json().get('messages', [])
            else:
                 print(f"[WARN] Failed to fetch history: {res.status_code}")
                 return []
        except Exception as e:
            print(f"[ERR] History Fetch Error: {e}")
            return []

# Singleton instance for easy import
dispatcher = SovereignDispatch()
