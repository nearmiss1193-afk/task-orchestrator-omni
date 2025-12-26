import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env.local")

def get_supabase() -> Client:
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def audit_millennium_wave():
    print("--- MISSION: MILLENNIUM WAVE AUDIT ---")
    supabase = get_supabase()
    
    # Check status counts for millennium leads
    res = supabase.table("contacts_master").select("status").ilike("ghl_contact_id", "millen_%").execute()
    
    stats = {}
    if res.data:
        for r in res.data:
            s = r['status']
            stats[s] = stats.get(s, 0) + 1
            
    print(f"Total Millennium Leads Analyzed: {len(res.data) if res.data else 0}")
    print(f"Stats by Status: {stats}")
    
    # Check for recent logs
    logs = supabase.table("brain_logs").select("*").order("timestamp", desc=True).limit(10).execute()
    print("\n--- RECENT CLOUD LOGS ---")
    if logs.data:
        for l in logs.data:
            print(f"[{l['timestamp']}] {l['message']}")
    else:
        print("No recent logs found.")

if __name__ == "__main__":
    audit_millennium_wave()
