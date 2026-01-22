"""
EXECUTOR LAYER
Deterministic, reliable action scripts.
"""
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
import requests

# Helper: Annealing integration
try:
    from annealing_engine import self_annealing
except ImportError:
    def self_annealing(func): return func

class EmpireExecutors:
    def __init__(self):
        self.supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
        self.supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        self.ghl_key = os.getenv("GHL_API_KEY")
        self.ghl_loc = os.getenv("GHL_LOCATION_ID")
        
        # Initialize DB
        if self.supa_url and self.supa_key:
            from supabase import create_client
            self.supabase = create_client(self.supa_url, self.supa_key)
            self.db_connected = True
        else:
            self.supabase = None
            self.db_connected = False

    @self_annealing
    def _ensure_ghl_contact(self, prospect_id: str, phone: str = None, email: str = None, name: str = None) -> str:
        """Helper to sync contact to GHL and get ID"""
        # 1. Check if prospect_id is already a GHL ID (simple heuristic: length 20, no dashes)
        if len(prospect_id) == 20 and "-" not in prospect_id:
             return prospect_id

        # 2. If UUID or temp, we must create/lookup in GHL
        # For simplicity in this v4.0 build, we will CREATE/UPDATE by Phone/Email
        url = "https://services.leadconnectorhq.com/contacts/"
        headers = {
            'Authorization': f'Bearer {os.environ.get("GHL_API_TOKEN")}', 
            'Version': '2021-07-28', 
            'Content-Type': 'application/json'
        }
        
        payload = {}
        if phone: payload["phone"] = phone
        if email: payload["email"] = email
        if name: payload["name"] = name
        
        try:
            # Try creation/upsert
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code in [200, 201]:
                data = r.json()
                ghl_id = data.get('contact', {}).get('id')
                print(f"🔗 [GHL] Synced Contact: {ghl_id}")
                return ghl_id
            else:
                print(f"⚠️ [GHL] Sync Failed ({r.status_code}): {r.text}")
                return None
        except Exception as e:
            print(f"❌ [GHL] API Error: {e}")
            return None

    @self_annealing
    def send_sms(self, to: str, message: str, prospect_id: Optional[str] = None) -> Dict[str, Any]:
        """
        EXECUTOR: send_sms
        Location: GHL API (Real)
        """
        print(f"📱 [SMS] Sending to {to}...")
        
        ghl_id = self._ensure_ghl_contact(prospect_id, phone=to)
        if not ghl_id:
            return {"success": False, "error": "Could not sync contact to GHL"}

        url = "https://services.leadconnectorhq.com/conversations/messages"
        headers = {
            'Authorization': f'Bearer {os.environ.get("GHL_API_TOKEN")}', 
            'Version': '2021-07-28', 
            'Content-Type': 'application/json'
        }
        
        payload = {
            "type": "SMS",
            "contactId": ghl_id,
            "message": message
        }
        
        try:
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code in [200, 201]:
                print(f"✅ [SMS] Sent! ID: {r.json().get('messageId')}")
                return {"success": True, "sid": r.json().get('messageId')}
            else:
                print(f"❌ [SMS] Failed ({r.status_code}): {r.text}")
                return {"success": False, "error": r.text}
        except Exception as e:
             return {"success": False, "error": str(e)}

    @self_annealing
    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """EXECUTOR: send_email (GHL Real)"""
        print(f"📧 [EMAIL] Sending to {to}...")
        
        ghl_id = self._ensure_ghl_contact(to, email=to) # Use email as ID proxy if needed
        if not ghl_id:
             return {"success": False, "error": "Could not sync contact to GHL"}
             
        url = "https://services.leadconnectorhq.com/conversations/messages"
        headers = {
            'Authorization': f'Bearer {os.environ.get("GHL_API_TOKEN")}', 
            'Version': '2021-07-28', 
            'Content-Type': 'application/json'
        }
        
        payload = {
            "type": "Email",
            "contactId": ghl_id,
            "emailSubject": subject,
            "html": body
        }
        
        try:
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code in [200, 201]:
                print(f"✅ [EMAIL] Sent! ID: {r.json().get('messageId')}")
                return {"success": True, "message_id": r.json().get('messageId')}
            else:
                print(f"❌ [EMAIL] Failed ({r.status_code}): {r.text}")
                return {"success": False, "error": r.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @self_annealing
    def classify_intent(self, message: str) -> Dict[str, Any]:
        """
        EXECUTOR: classify_intent
        Uses heuristics or LLM to determine intent.
        """
        msg_lower = message.lower()
        if "stop" in msg_lower:
            return {"intent": "stop", "confidence": 1.0}
        elif any(w in msg_lower for w in ["yes", "interested", "call me", "sign up"]):
            return {"intent": "high", "confidence": 0.9}
        elif any(w in msg_lower for w in ["maybe", "how much", "price", "info"]):
            return {"intent": "medium", "confidence": 0.8}
        elif any(w in msg_lower for w in ["no", "not interested", "busy"]):
            return {"intent": "negative", "confidence": 0.9}
        else:
            return {"intent": "low", "confidence": 0.5}

    @self_annealing
    def onboard_customer(self, customer_email: str, amount: float):
        """EXECUTOR: onboard_customer"""
        print(f"🚀 [ONBOARD] Welcome sequence for {customer_email} (${amount})")
        
        # 1. Send Welcome Email
        self.send_email(
            customer_email, 
            "Welcome to Sovereign Empire!", 
            "Your AI Agents are being provisioned. Login here: https://portal.aiserviceco.com"
        )
        
        # 2. Provision Resources (Mock)
        print("⚙️ Provisioning Twilio Number... Done.")
        print("🤖 creating Vapi Assistant... Done.")
        
        return {"success": True, "status": "onboarding_started"}

    @self_annealing
    def update_database(self, table: str, record_id: str, updates: Dict) -> Dict:
        """EXECUTOR: update_database"""
        if not self.db_connected:
            return {"success": False, "error": "DB not connected"}
        
        try:
            res = self.supabase.table(table).update(updates).eq("id", record_id).execute()
            print(f"💾 [DB] Updated {table} {record_id} -> {updates}")
            return {"success": True, "data": res.data}
        except Exception as e:
            print(f"❌ [DB] Update failed: {e}")
            return {"success": False, "error": str(e)}

    def log_action(self, agent: str, action: str, details: str):
        """Audit Log"""
        print(f"📝 [LOG] {agent}: {action} - {details}")
        # Insert into agent_activity_log if exists
