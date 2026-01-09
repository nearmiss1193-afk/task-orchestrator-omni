import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fix_stuck_leads():
    print("SCANNING FOR STUCK LEADS...")
    try:
        # Find leads stuck in processing_email
        res = supabase.table("leads").select("*").eq("status", "processing_email").execute()
        stuck = res.data
        
        if not stuck:
            print("No stuck leads found.")
            return

        print(f"Found {len(stuck)} stuck leads. Resetting to 'ready_to_send'...")
        
        for lead in stuck:
            supabase.table("leads").update({
                "status": "ready_to_send"
            }).eq("id", lead['id']).execute()
            print(f"  Reset {lead['company_name']}")
            
        print("RECOVERY COMPLETE.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_stuck_leads()
