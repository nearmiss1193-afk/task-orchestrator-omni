
import os
from supabase import create_client
import json

# Hardcoded Credentials (The good ones)
VAULT = {
    "SUPABASE_URL": "https://rzcpfwkygdvoshtwxncs.supabase.co",
    "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
}

def inspect():
    try:
        supabase = create_client(VAULT["SUPABASE_URL"], VAULT["SUPABASE_SERVICE_ROLE_KEY"])
        
        print("--- INSPECTING SCHEMA: contacts_master ---")
        # Attempt to insert a dummy row to get a clear error about missing columns, 
        # OR select one row and print keys if data exists.
        
        res = supabase.table("contacts_master").select("*").limit(1).execute()
        if res.data:
            print("Found existing data. Columns:")
            print(json.dumps(list(res.data[0].keys()), indent=2))
        else:
            print("Table empty. Attempting insertion of empty dict to trigger schema error (common hack) or just assuming standard columns.")
            # If empty, we can't easily get columns via postgrest without info endpoint, 
            # but we can try to assume standard ones or read previous code.
            # Let's try to read deployment code for this table if this fails.
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
