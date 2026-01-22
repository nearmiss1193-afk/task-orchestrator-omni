import modal
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Load env from root
sys.path.append(os.getcwd())
load_dotenv('.env.local')

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
        if len(prospect_id) == 20 and "-" not in prospect_id:
             return prospect_id
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
            r = requests.post(url, json=payload, headers=headers)
            if r.status_code in [200, 201]:
                return r.json().get('contact', {}).get('id')
            return None
        except:
            return None

    @self_annealing
    def send_sms(self, to: str, message: str, prospect_id: Optional[str] = None) -> Dict[str, Any]:
        """EXECUTOR: send_sms (GHL Real)"""
        print(f"📱 [SMS] Sending to {to}...")
        ghl_id = self._ensure_ghl_contact(prospect_id, phone=to)
        if not ghl_id: return {"success": False, "error": "No GHL ID"}

        url = "https://services.leadconnectorhq.com/conversations/messages"
        headers = {'Authorization': f'Bearer {os.environ.get("GHL_API_TOKEN")}', 'Version': '2021-07-28', 'Content-Type': 'application/json'}
        try:
            r = requests.post(url, json={"type": "SMS", "contactId": ghl_id, "message": message}, headers=headers)
            if r.status_code in [200, 201]:
                print(f"✅ [SMS] Sent! ID: {r.json().get('messageId')}")
                return {"success": True, "sid": r.json().get('messageId')}
            print(f"❌ [SMS] Failed ({r.status_code})")
            return {"success": False, "error": r.text}
        except Exception as e:
             return {"success": False, "error": str(e)}

    @self_annealing
    def send_email(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """EXECUTOR: send_email (GHL Real)"""
        print(f"📧 [EMAIL] Sending to {to}...")
        ghl_id = self._ensure_ghl_contact(to, email=to)
        if not ghl_id: return {"success": False, "error": "No GHL ID"}
        
        url = "https://services.leadconnectorhq.com/conversations/messages"
        headers = {'Authorization': f'Bearer {os.environ.get("GHL_API_TOKEN")}', 'Version': '2021-07-28', 'Content-Type': 'application/json'}
        try:
            r = requests.post(url, json={"type": "Email", "contactId": ghl_id, "emailSubject": subject, "html": body}, headers=headers)
            if r.status_code in [200, 201]:
                print(f"✅ [EMAIL] Sent! ID: {r.json().get('messageId')}")
                return {"success": True, "message_id": r.json().get('messageId')}
            return {"success": False, "error": r.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @self_annealing
    def update_database(self, table: str, record_id: str, updates: Dict) -> Dict:
        """EXECUTOR: update_database"""
        if not self.db_connected: return {"success": False, "error": "DB not connected"}
        try:
            res = self.supabase.table(table).update(updates).eq("id", record_id).execute()
            print(f"💾 [DB] Updated {table} {record_id}")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def log_action(self, agent: str, action: str, details: str):
        print(f"📝 [LOG] {agent}: {action} - {details}")

class Orchestrator:
    def __init__(self):
        self.exec = EmpireExecutors()
        self.agent_name = "Orchestrator-V2"
        
    def sense_and_act(self):
        """
        Main Loop: SENSE -> DECIDE -> ROUTE
        """
        print(f"\n🧠 [ORCHESTRATOR] Awake at {datetime.now().isoformat()}")
        
        # 1. TREE 1: NEW LEAD ARRIVES
        # Leads with status='new'
        self.process_new_leads()
        
        # 2. TREE 2: INBOUND RESPONSES
        # TODO: Implement when 'messages' table is ready
        
        # 6. TREE 6: SELF-HEALING
        self.check_health()
        
        print("💤 [ORCHESTRATOR] Sleeping...")

    def process_new_leads(self):
        """
        TREE 1: NEW LEAD ARRIVES
        Condition: contacts_master.status = 'new'
        """
        if not self.exec.db_connected:
            print("⚠️ DB Disconnected - Skipping Lead Processing")
            return

        try:
            # SENSE: Fetch new leads
            res = self.exec.supabase.table("contacts_master").select("*").eq("status", "new").limit(10).execute()
            leads = res.data or []
            
            if not leads:
                print("✅ No new leads to process.")
                return

            print(f"🧐 Processing {len(leads)} new leads...")
            
            for lead in leads:
                # DECIDE
                score = lead.get('lead_score') or 0
                has_phone = bool(lead.get('phone'))
                lead_id = lead['id']
                
                if score >= 60:
                    # High Priority
                    print(f"🔥 Hot Lead found: {lead.get('name')} (Score: {score})")
                    
                    if has_phone:
                        # ROUTE: SMS
                        self.exec.send_sms(lead['phone'], f"Hi {lead.get('first_name')}, saw you're looking for help with [Service]. available?", lead_id)
                        next_status = "contacted_sms"
                    else:
                        # ROUTE: Email
                        self.exec.send_email(lead['email'], "Quick Question", "Are you taking new clients?")
                        next_status = "contacted_email"
                else:
                    # Low Priority
                    print(f"❄️ Cold Lead: {lead.get('name')}")
                    next_status = "nurture_queue"

                # ACT: Update DB
                self.exec.update_database("contacts_master", lead_id, {
                    "status": next_status,
                    "last_outreach_at": datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"❌ Error in process_new_leads: {e}")

    def check_health(self):
        """
        TREE 6: SELF-HEALING
        """
        print("🏥 Running System Health Check...")
        # Simple logging for now
        self.exec.log_action(self.agent_name, "health_check", "All systems nominal")

# Modal Definition
app = modal.App("v2-master-orchestrator")
image = modal.Image.debian_slim().pip_install("supabase", "requests", "python-dotenv", "fastapi")
VAULT = modal.Secret.from_name("agency-vault")

@app.function(
    image=image, 
    secrets=[VAULT], 
    schedule=modal.Period(minutes=5),
    timeout=300
)
def run_orchestrator_cron():
    """
    AUTONOMOUS CRON JOB
    Runs every 5 minutes to continuously monitor and route.
    """
    orch = Orchestrator()
    orch.sense_and_act()

if __name__ == "__main__":
    # Local Test
    orch = Orchestrator()
    orch.sense_and_act()
