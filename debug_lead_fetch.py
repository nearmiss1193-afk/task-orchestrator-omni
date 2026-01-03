
import os
from supabase import create_client
import json

# HARDCODED SECRETS
URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

def get_supabase():
    return create_client(URL, KEY)

def debug_fetch():
    print("--- DEBUGGING LEAD FETCH ---")
    sb = get_supabase()
    
    # 1. Get a sample row
    res = sb.table("contacts_master").select("*").limit(1).execute()
    if not res.data:
        print("❌ DB Empty")
        return
        
    row = res.data[0]
    real_ghl_id = row.get("ghl_contact_id")
    print(f"Sample Row ID: {real_ghl_id} (Type: {type(real_ghl_id)})")
    
    # 2. Try to fetch it back strictly
    print(f"Attempting fetch with .eq('ghl_contact_id', '{real_ghl_id}')...")
    
    # Try as string
    try:
        q1 = sb.table("contacts_master").select("*").eq("ghl_contact_id", str(real_ghl_id)).execute()
        print(f"Query as STRING found: {len(q1.data)}")
    except Exception as e:
        print(f"Query as STRING failed: {e}")

    # Try as int (if applicable)
    if isinstance(real_ghl_id, int) or (isinstance(real_ghl_id, str) and real_ghl_id.isdigit()):
        try:
            q2 = sb.table("contacts_master").select("*").eq("ghl_contact_id", int(real_ghl_id)).execute()
            print(f"Query as INT found: {len(q2.data)}")
        except Exception as e:
            print(f"Query as INT failed: {e}")

if __name__ == "__main__":
    debug_fetch()
