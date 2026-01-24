import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.getcwd())
load_dotenv('.env.local')

def check_outbound():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    supabase = create_client(url, key)
    
    print("\\n=== Checking outbound_touches table ===")
    try:
        res = supabase.table("outbound_touches").select("*").order("created_at", desc=True).limit(10).execute()
        if res.data:
            for row in res.data:
                print(f"  {row.get('created_at')} | {row.get('channel')} | {row.get('status')}")
        else:
            print("  No records in outbound_touches.")
    except Exception as e:
        print(f"  Error: {e}")
        
    print("\\n=== Checking contacts_master for any last_contacted_at ===")
    try:
        res = supabase.table("contacts_master").select("full_name, status, last_contacted_at").order("last_contacted_at", desc=True).limit(5).execute()
        if res.data:
            for row in res.data:
                print(f"  {row.get('last_contacted_at')} | {row.get('full_name')} | {row.get('status')}")
        else:
            print("  No records with last_contacted_at.")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    check_outbound()
