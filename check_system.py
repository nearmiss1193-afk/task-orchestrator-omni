"""Manually trigger a prospector run and check system health"""
import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
from datetime import datetime, timezone

sb = get_supabase()

with open("system_health.txt", "w") as f:
    # Heartbeat check
    hb = sb.table("system_health_log").select("*").order("checked_at", desc=True).limit(5).execute()
    f.write("=== HEARTBEAT ===\n")
    for h in (hb.data or []):
        f.write(f"  {h.get('checked_at','')} | {h.get('status','')}\n")
    
    # Prospector last run
    pr = sb.table("system_state").select("*").eq("key", "prospector_last_run").execute()
    f.write(f"\n=== PROSPECTOR ===\n")
    if pr.data:
        f.write(f"  Last run: {pr.data[0].get('status','?')}\n")
    else:
        f.write("  Last run: NOT RECORDED\n")
    
    # Campaign mode
    cm = sb.table("system_state").select("*").eq("key", "campaign_mode").execute()
    f.write(f"\n=== CAMPAIGN ===\n")
    if cm.data:
        f.write(f"  Mode: {cm.data[0].get('status','?')}\n")
    
    # Outreach recent
    ot = sb.table("outbound_touches").select("*").order("ts", desc=True).limit(3).execute()
    f.write(f"\n=== RECENT OUTREACH ===\n")
    for t in (ot.data or []):
        f.write(f"  {t.get('ts','')} | {t.get('channel','')} | {t.get('status','')} | {t.get('company','')}\n")
    
    # Total contacts
    total = sb.table("contacts_master").select("*", count="exact").eq("status", "new").execute()
    f.write(f"\n=== PIPELINE ===\n")
    f.write(f"  New leads ready: {total.count}\n")

print("Written to system_health.txt")
