import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase Env Vars")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_test_lead():
    user_phone = "+13527585336" # User's verified number
    
    import uuid
    
    data = {
        "id": str(uuid.uuid4()),
        "company_name": "Boss Test Roofing",
        "status": "ready_to_send",
        "agent_research": {
            "phone": user_phone,
            "name": "Boss",
            "city": "Test City",
            "state": "FL"
        }
    }
    
    try:
        # Check if exists
        existing = supabase.table("leads").select("id").eq("phone", user_phone).execute()
        if existing.data and len(existing.data) > 0:
            lead_id = existing.data[0]['id']
            print(f"Lead Exists: {lead_id}")
            # Reset status
            supabase.table("leads").update({"status": "ready_to_send"}).eq("id", lead_id).execute()
            return lead_id

        # Insert if new
        res = supabase.table("leads").insert(data).execute()
        if res.data:
            lead = res.data[0]
            print(f"Created Test Lead: {lead['id']}")
            return lead['id']
        else:
            print("Failed to create lead.")
            return None
    except Exception as e:
         print(f"Error: {e}")
         return None

if __name__ == "__main__":
    create_test_lead()
