import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_any_lead():
    try:
        # Fetch one lead
        res = supabase.table("leads").select("*").limit(1).execute()
        
        if res.data and len(res.data) > 0:
            lead = res.data[0]
            lead_id = lead['id']
            print(f"FOUND_LEAD_ID: {lead_id}")
            with open("temp_lead_id.txt", "w") as f:
                f.write(lead_id)
            return lead_id
        else:
            print("No leads found in DB.")
            return None
    except Exception as e:
        print(f"DB Error: {e}")
        return None

if __name__ == "__main__":
    fetch_any_lead()
