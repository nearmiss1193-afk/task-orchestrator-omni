import requests
import json

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
# Key from temp_env.txt (decoded verified as service_role)
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

def verify_tables():
    print(f"[VERIFY] Checking Supabase: {SUPABASE_URL}")
    
    tables = ["contact_profiles", "conversations", "conversation_events", "job_locks"]
    missing = []
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "return=representation"
    }
    
    for table in tables:
        try:
            # Try to select 1 row (limit=1)
            # If table doesn't exist, Supabase returns 404
            url = f"{SUPABASE_URL}/rest/v1/{table}?limit=1"
            r = requests.get(url, headers=headers, timeout=5)
            
            if r.status_code == 200:
                print(f"[VERIFY] ✅ Table '{table}' exists.")
            elif r.status_code == 404:
                print(f"[VERIFY] ❌ Table '{table}' MISSING (404).")
                missing.append(table)
            else:
                print(f"[VERIFY] ⚠️ Table '{table}' error: {r.status_code}")
                # 400 often means "relation does not exist" in some contexts or invalid syntax, 
                # but Supabase REST usually returns 404 for missing table.
                if "relation" in r.text and "does not exist" in r.text:
                     print(f"[VERIFY] ❌ Table '{table}' DOES NOT EXIST.")
                     missing.append(table)
                else:
                     # Log text for debug
                     print(f"      Response: {r.text[:200]}")
                
        except Exception as e:
            print(f"[VERIFY] ❌ Exception checking '{table}': {e}")
            missing.append(table)
            
    if missing:
        print(f"\n[VERIFY] FATAL: Missing tables: {missing}")
        print("[VERIFY] ACTION REQUIRED: Run 'supabase_memory_schema.sql' in the Supabase SQL Editor.")
    else:
        print("\n[VERIFY] ✅ All tables exist.")

if __name__ == "__main__":
    verify_tables()
