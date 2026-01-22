import os
import json
from supabase import create_client, Client

# Hardcoded from secrets_export.json for health check
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

def check_health():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("--- RECENT BRAIN LOGS (Last 10) ---")
        logs = supabase.table('brain_logs').select('*').order('timestamp', desc=True).limit(10).execute()
        for log in logs.data:
            print(f"[{log.get('timestamp')}] {log.get('level', 'INFO').upper()}: {log.get('message')}")
            
        print("\n--- ERROR LOGS (Last 5) ---")
        errors = supabase.table('brain_logs').select('*').eq('level', 'error').order('timestamp', desc=True).limit(5).execute()
        for err in errors.data:
            print(f"[{err.get('timestamp')}] ERROR: {err.get('message')}")
            
        print("\n--- RECENT CONTACT ACTIVITY ---")
        contacts = supabase.table('contacts_master').select('name, last_response_at, status').order('last_response_at', desc=True).limit(5).execute()
        for c in contacts.data:
            print(f"Contact: {c.get('name')} | Last Activity: {c.get('last_response_at')} | Status: {c.get('status')}")

    except Exception as e:
        print(f"Health check failed: {e}")

if __name__ == "__main__":
    check_health()
