import os
import json
import datetime
from supabase import create_client, Client

url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
supabase: Client = create_client(url, key)

def check_truth():
    print("--- TRUTH CHECK (HARDENING VERIFIER) ---")
    
    # 1. Check System State
    try:
        state = supabase.table("system_state").select("*").execute()
        print("\n[SYSTEM STATE]")
        for row in state.data:
            print(f"Key: {row.get('key')} | Status: {row.get('status')} | Value: {row.get('value')}")
    except Exception as e:
        print(f"Error checking system_state: {e}")

    # 2. Check Contacts
    try:
        contacts = supabase.table("contacts_master").select("status", count="exact").execute()
        print(f"\n[CONTACTS] Total: {contacts.count}")
        # Group by status manually if needed, but for now just status check
    except Exception as e:
        print(f"Error checking contacts: {e}")

    # 3. Check Heartbeats
    try:
        health = supabase.table("system_health_log").select("*").order("checked_at", desc=True).limit(5).execute()
        print("\n[HEARTBEATS]")
        for row in health.data:
            print(f"Time: {row['checked_at']} | Status: {row['status']}")
    except Exception as e:
        print(f"Error checking health: {e}")

    # 4. Check Outreach (THE TRUTH)
    try:
        touches = supabase.table("outbound_touches").select("*", count="exact").order("ts", desc=True).limit(5).execute()
        print(f"\n[OUTREACH] Total: {touches.count}")
        for row in touches.data:
            print(f"Time: {row['ts']} | Channel: {row['channel']} | Lead: {row.get('contact_id')}")
    except Exception as e:
        print(f"Error checking outreach: {e}")

if __name__ == "__main__":
    check_truth()
