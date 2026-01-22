import os
import json
from supabase import create_client, Client

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

def check_health():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test connection by listing tables if possible or just picking one
        print("--- TESTING SUPABASE CONNECTION ---")
        
        # Checking brain_logs
        print("\n--- BRAIN LOGS ---")
        try:
            logs = supabase.table('brain_logs').select('*').order('timestamp', desc=True).limit(10).execute()
            if logs.data:
                for log in logs.data:
                    print(f"[{log.get('timestamp')}] {log.get('level', 'INFO').upper()}: {log.get('message')}")
            else:
                print("No brain logs found.")
        except Exception as e:
            print(f"Error reading brain_logs: {e}")

        # Checking staged_replies
        print("\n--- STAGED REPLIES ---")
        try:
            replies = supabase.table('staged_replies').select('*').order('created_at', desc=True).limit(5).execute()
            if replies.data:
                for r in replies.data:
                    print(f"Reply ID: {r.get('id')} | Status: {r.get('status')} | Created: {r.get('created_at')}")
            else:
                print("No staged replies found.")
        except Exception as e:
            print(f"Error reading staged_replies: {e}")

        # Checking system_health (if it exists)
        print("\n--- SYSTEM STATUS ---")
        try:
            status = supabase.table('system_status').select('*').limit(1).execute()
            if status.data:
                print(f"System Status: {status.data[0]}")
            else:
                print("No system status entry.")
        except Exception as e:
            print(f"Error reading system_status: {e}")

    except Exception as e:
        print(f"Global check failed: {e}")

if __name__ == "__main__":
    check_health()
