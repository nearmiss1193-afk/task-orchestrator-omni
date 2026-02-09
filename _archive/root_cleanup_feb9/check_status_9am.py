import os
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
from datetime import datetime, timezone, timedelta

def check():
    sb = get_supabase()
    if not sb:
        print("❌ Supabase connection failed")
        return

    # 1. Heartbeat
    hb = sb.table("system_health_log").select("checked_at").order("checked_at", desc=True).limit(1).execute()
    last_hb = hb.data[0]['checked_at'] if hb.data else "NEVER"
    print(f"💓 LAST HEARTBEAT: {last_hb}")

    # 2. Campaign Mode
    state = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
    mode = state.data[0]['status'] if state.data else "NOT FOUND"
    print(f"📡 CAMPAIGN MODE: {mode}")

    # 3. Outreach in last 60 mins
    # 9:00 AM wave should show up here
    now_utc = datetime.now(timezone.utc)
    one_hour_ago = (now_utc - timedelta(hours=1)).isoformat()
    outreach = sb.table("outbound_touches").select("id", count="exact").gt("ts", one_hour_ago).execute()
    print(f"🚀 OUTREACH (LAST HOUR): {outreach.count}")

    # 4. Success/Failure split
    touches = sb.table("outbound_touches").select("status").gt("ts", one_hour_ago).execute()
    if touches.data:
        success = len([t for t in touches.data if t['status'] not in ['failed', 'error']])
        fail = len([t for t in touches.data if t['status'] in ['failed', 'error']])
        print(f"📊 SPLIT: {success} Success / {fail} Fail")
    
    # 5. Leads ready
    ready = sb.table("contacts_master").select("id", count="exact").eq("status", "research_done").execute()
    print(f"📈 LEADS READY: {ready.count}")

if __name__ == "__main__":
    check()
