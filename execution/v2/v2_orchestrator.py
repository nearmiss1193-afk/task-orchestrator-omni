"""
🏛️ ORCHESTRATOR (LAYER 2)
The autonomous brain of the Empire.
Runs every 5 minutes (via Cron or Loop).
"""
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Load env from root
sys.path.append(os.getcwd())
load_dotenv('.env.local')

from execution.v2.executors import EmpireExecutors

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

import modal

# Modal Definition
app = modal.App("v2-master-orchestrator")
image = modal.Image.debian_slim().pip_install("supabase", "requests", "python-dotenv")
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
