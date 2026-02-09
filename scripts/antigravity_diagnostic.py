import os
import asyncio
from supabase import create_client, Client
from datetime import datetime, timedelta, timezone

async def verify_status():
    url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    # Using the service role key from .env (found in previous step)
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
    supabase: Client = create_client(url, key)

    print("\n" + "="*50)
    print("⚫ ANTIGRAVITY v5.0 - OPERATIONAL DIAGNOSTIC")
    print("="*50 + "\n")

    # 1. Outreach Truth Test
    try:
        thirty_mins_ago = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
        touches = supabase.table("outbound_touches").select("*").gt("ts", thirty_mins_ago).execute()
        sent_count = len(touches.data)
        print(f"□ [1] Outreach (30m): {'✅' if sent_count > 0 else '❌'} ({sent_count} sent)")
    except Exception as e:
        print(f"□ [1] Outreach (30m): ❌ (Error querying outbound_touches: {e})")

    # 2. Heartbeat check
    try:
        fifteen_mins_ago = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        heartbeats = supabase.table("system_health_log").select("*").gt("checked_at", fifteen_mins_ago).order("checked_at", desc=True).limit(5).execute()
        hb_count = len(heartbeats.data)
        print(f"□ [2] Heartbeat (15m): {'✅' if hb_count > 0 else '❌'} ({hb_count} beats recorded)")
    except Exception as e:
        print(f"□ [2] Heartbeat (15m): ❌ (Error querying system_health_log: {e})")

    # 3. Campaign Mode
    try:
        state = supabase.table("system_state").select("*").eq("key", "campaign_mode").execute()
        mode = state.data[0]['status'] if state.data else 'unknown'
        print(f"□ [3] Campaign Mode: {'✅' if mode == 'working' else '❌'} ({mode})")
    except Exception as e:
        print(f"□ [3] Campaign Mode: ❌ (Error querying system_state: {e})")

    # 4. Lead Availability
    try:
        leads = supabase.table("contacts_master").select("status").execute()
        status_counts = {}
        for l in leads.data:
            s = l['status']
            status_counts[s] = status_counts.get(s, 0) + 1
        contactable = status_counts.get('new', 0) + status_counts.get('research_done', 0)
        print(f"□ [4] Contactable Leads: {'✅' if contactable > 0 else '❌'} ({contactable} total)")
        print(f"    (Breakdown: {status_counts})")
    except Exception as e:
        print(f"□ [4] Contactable Leads: ❌ (Error: {e})")

    print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(verify_status())
