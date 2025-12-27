
import os
from supabase import create_client
import time

# Load Env
try:
    with open("modules/orchestrator/dashboard/.env.local", "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                # Handle spaces or quotes if needed, simplified here
                if key == "NEXT_PUBLIC_SUPABASE_URL": os.environ["SUPABASE_URL"] = val.strip().strip('"')
                if key == "SUPABASE_SERVICE_ROLE_KEY": os.environ["SUPABASE_SERVICE_ROLE_KEY"] = val.strip().strip('"')
except:
    pass

def seed():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("CRITICAL: Missing credentials.")
        return

    supabase = create_client(url, key)
    print("--- SEEDING TEST DATA ---")

    # Insert Leads
    leads = [
        {"name": "Alpha Corp", "company": "Alpha", "score": 85, "email": "ceo@alpha.com"},
        {"name": "Beta Ltd", "company": "Beta", "score": 90, "email": "vp@beta.com"},
        {"name": "Gamma Inc", "company": "Gamma", "score": 85, "email": "owner@gamma.com"},
        {"name": "Delta LLC", "company": "Delta", "score": 95, "email": "admin@delta.com"},
        {"name": "Omega Co", "company": "Omega", "score": 85, "email": "founder@omega.com"}
    ]
    
    # Try inserting into 'leads' first, then 'contacts_master'
    target_table = "leads"
    try:
        # Check if table exists by selecting 1
        supabase.table("leads").select("*").limit(1).execute()
    except:
        print("Table 'leads' not found. Using 'contacts_master'.")
        target_table = "contacts_master"

    print(f"Targeting Table: {target_table}")
    
    for lead in leads:
        try:
            # Adjust payload for contacts_master if needed
            payload = lead
            if target_table == "contacts_master":
                payload = {
                    "first_name": lead["name"].split()[0],
                    "last_name": lead["name"].split()[-1] if " " in lead["name"] else "",
                    "company_name": lead["company"],
                    "email": lead["email"],
                    # score might not exist in contacts_master schema, skipping
                }
            
            res = supabase.table(target_table).insert(payload).execute()
            print(f"Inserted: {lead['name']}")
            
            # Log action
            log_payload = {
                "message": f"SYSTEM: Ingested high-value lead {lead['name']} (Score: {lead['score']})",
                "component": "LeadsEngine"
            }
            supabase.table("brain_logs").insert(log_payload).execute()

        except Exception as e:
            print(f"Failed to insert {lead['name']}: {e}")

if __name__ == "__main__":
    seed()
