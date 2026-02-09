import os
from supabase import create_client, Client
from datetime import datetime, timedelta

url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
supabase: Client = create_client(url, key)

def check_status():
    print("═══════════════════════════════════════════════════════════════")
    print("SYSTEM HEALTH DIAGNOSTIC")
    print("═══════════════════════════════════════════════════════════════\n")

    # 1. Campaign Mode
    state = supabase.table("system_state").select("*").eq("key", "campaign_mode").execute()
    mode = state.data[0]['value'] if state.data else "UNKNOWN"
    print(f"□ Campaign Mode: {mode}")

    # 2. Heartbeat (Last 30 min)
    heartbeat = supabase.table("system_health_log").select("*").order("checked_at", desc=True).limit(1).execute()
    if heartbeat.data:
        last_hb = heartbeat.data[0]['checked_at']
        print(f"□ Last Heartbeat: {last_hb}")
    else:
        print("□ Last Heartbeat: NONE FOUND")

    # 3. Outreach (Last 30 min)
    half_hour_ago = (datetime.now() - timedelta(minutes=30)).isoformat()
    outreach = supabase.table("outbound_touches").select("id", count="exact").gt("ts", half_hour_ago).execute()
    print(f"□ Outreach (30m): {outreach.count} sent")

    # 4. Contacts Status
    contacts = supabase.table("contacts_master").select("status", count="exact").execute()
    print(f"\nContacts Summary:")
    # Group manually if needed, but let's just show total for now
    total_contacts = supabase.table("contacts_master").select("id", count="exact").limit(1).execute()
    print(f"□ Total Contacts: {total_contacts.count}")
    
    # 5. Cron Count in deploy.py
    if os.path.exists("deploy.py"):
        with open("deploy.py", "r") as f:
            content = f.read()
            cron_count = content.count("schedule=modal")
            print(f"□ Cron Count (deploy.py): {cron_count}")
    
    print("\n═══════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    check_status()
