"""Dump full verification to file"""
import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
from datetime import datetime, timezone

sb = get_supabase()

with open("verify_output.txt", "w") as f:
    f.write(f"Check time: {datetime.now(timezone.utc).isoformat()}\n\n")
    
    hb = sb.table("system_health_log").select("checked_at,status").order("checked_at", desc=True).limit(5).execute()
    f.write("=== HEARTBEATS ===\n")
    for h in (hb.data or []):
        ts = h.get('checked_at','')
        try:
            t = datetime.fromisoformat(ts.replace('Z','+00:00'))
            age = (datetime.now(timezone.utc) - t).total_seconds() / 60
            f.write(f"  {ts} | {h.get('status','')} | {age:.0f} min ago\n")
        except:
            f.write(f"  {ts} | {h.get('status','')}\n")

    pr = sb.table("system_state").select("*").eq("key", "prospector_last_run").execute()
    f.write("\n=== PROSPECTOR ===\n")
    if pr.data:
        row = pr.data[0]
        f.write(f"  Status: {row.get('status','')} | Timestamp: {row.get('last_error','')}\n")
    
    pc = sb.table("system_health_log").select("checked_at").eq("status", "prospecting_complete").order("checked_at", desc=True).limit(3).execute()
    f.write(f"\n=== PROSPECTING RUNS: {len(pc.data)} ===\n")
    
    lt = sb.table("outbound_touches").select("ts,channel,status").order("ts", desc=True).limit(3).execute()
    f.write(f"\n=== LATEST OUTREACH ===\n")
    for t in (lt.data or []):
        f.write(f"  {t.get('ts','')} | {t.get('channel','')} | {t.get('status','')}\n")

print("Written to verify_output.txt")
