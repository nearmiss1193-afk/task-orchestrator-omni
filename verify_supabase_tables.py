import os
import requests
import json

# Setup env (same as app.py)
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

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
                print(f"[VERIFY] ⚠️ Table '{table}' error: {r.status_code} {r.text}")
                missing.append(table)
                
        except Exception as e:
            print(f"[VERIFY] ❌ Exception checking '{table}': {e}")
            missing.append(table)
            
    if missing:
        print(f"\n[VERIFY] FATAL: The following tables are missing or inaccessible: {missing}")
        print("[VERIFY] You MUST run the 'supabase_memory_schema.sql' in the Supabase SQL Editor.")
    else:
        print("\n[VERIFY] ✅ All tables exist and are accessible.")

if __name__ == "__main__":
    verify_tables()
