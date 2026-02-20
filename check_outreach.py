import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

sb = get_supabase()

with open("outreach_status.txt", "w") as f:
    # Campaign mode
    cm = sb.table("system_state").select("*").eq("key", "campaign_mode").execute()
    f.write(f"Campaign mode: {cm.data[0].get('status','?') if cm.data else 'NOT SET'}\n")
    
    # Outreach today
    ot = sb.table("outbound_touches").select("*", count="exact").gte("ts", "2026-02-19T00:00:00").execute()
    f.write(f"Outreach today (Feb 19): {ot.count}\n")
    if ot.data:
        for t in ot.data[:5]:
            f.write(f"  {t.get('ts','')} | {t.get('channel','')} | {t.get('lead_id','')[:12]}...\n")
    
    # Last 7 days
    ot7 = sb.table("outbound_touches").select("*", count="exact").gte("ts", "2026-02-12T00:00:00").execute()
    f.write(f"Outreach last 7 days: {ot7.count}\n")
    
    # Heartbeat
    hb = sb.table("system_health_log").select("*").order("checked_at", desc=True).limit(1).execute()
    if hb.data:
        f.write(f"Last heartbeat: {hb.data[0].get('checked_at','')} | Status: {hb.data[0].get('status','')}\n")
    
    # Leads ready
    jax_new = sb.table("contacts_master").select("*", count="exact").eq("lead_source", "manus_jacksonville").eq("status", "new").execute()
    all_new = sb.table("contacts_master").select("*", count="exact").eq("status", "new").execute()
    f.write(f"\nJacksonville leads ready (new): {jax_new.count}\n")
    f.write(f"Total leads ready (new): {all_new.count}\n")

print("Written to outreach_status.txt")
