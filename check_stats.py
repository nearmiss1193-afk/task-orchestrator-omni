import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: Supabase credentials missing.")
    exit()

supabase = create_client(url, key)

try:
    # 1. Total Leads
    res_leads = supabase.table("leads").select("*", count="exact").execute()
    total = res_leads.count
    
    # 2. Leads with Audit Links (Ready Reports)
    # Note: 'neq' means Not Equal. We want where audit_link is NOT null/empty.
    # Supabase filter syntax might vary, let's try fetching and python counting for accuracy if small, 
    # but 'neq' to empty string is safer.
    res_audits = supabase.table("leads").select("*", count="exact").neq("audit_link", "").execute()
    ready = res_audits.count
    
    print(f"STATS_TOTAL_PROSPECTS={total}")
    print(f"STATS_READY_REPORTS={ready}")
    
except Exception as e:
    print(f"Error querying DB: {e}")
