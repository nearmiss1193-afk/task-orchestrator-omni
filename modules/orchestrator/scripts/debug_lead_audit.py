import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env.local")

def get_supabase() -> Client:
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def simple_audit():
    print("--- MISSION: SIMPLE LEAD AUDIT ---")
    supabase = get_supabase()
    
    # Check total count
    res = supabase.table("contacts_master").select("ghl_contact_id, status").limit(10).execute()
    print(f"Sample Leads: {res.data}")
    
    # Check millennium specifically
    millen_res = supabase.table("contacts_master").select("status").ilike("ghl_contact_id", "millen%").execute()
    print(f"Total Millennium Leads: {len(millen_res.data) if millen_res.data else 0}")
    
    if millen_res.data:
        stats = {}
        for r in millen_res.data:
            s = r['status']
            stats[s] = stats.get(s, 0) + 1
        print(f"Millennium Stats: {stats}")

if __name__ == "__main__":
    simple_audit()
