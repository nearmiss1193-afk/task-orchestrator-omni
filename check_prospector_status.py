"""Check prospector status — when did it last run and what was the result?"""
import sys
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

sb = get_supabase()

with open("prospector_status.txt", "w") as f:
    # Last run timestamp
    last_run = sb.table("system_state").select("*").eq("key", "prospector_last_run").execute()
    if last_run.data:
        f.write(f"Last run: {last_run.data[0].get('status','?')}\n")
    else:
        f.write("Last run: NOT RECORDED\n")
    
    # Cycle index 
    idx = sb.table("system_state").select("*").eq("key", "prospector_cycle_index").execute()
    if idx.data:
        f.write(f"Cycle index: {idx.data[0].get('last_error','?')}\n")
    else:
        f.write("Cycle index: NOT SET\n")
    
    # Total matrix size: 57 niches x 17 cities = 969
    f.write(f"Total matrix: 57 niches x 17 cities = 969 combos\n")
    
    # Recent prospecting health logs
    logs = sb.table("system_health_log").select("*").eq("status", "prospecting_complete").order("checked_at", desc=True).limit(5).execute()
    f.write(f"\nRecent prospecting runs: {len(logs.data)}\n")
    for l in (logs.data or []):
        f.write(f"  {l.get('checked_at','')} | {l.get('details','')}\n")
    
    # How many google_places leads in DB?
    gp = sb.table("contacts_master").select("*", count="exact").eq("lead_source", "google_places").execute()
    f.write(f"\nTotal google_places leads in DB: {gp.count}\n")
    
    # By status
    for status in ["new", "outreach_sent", "sequence_complete", "bad_data"]:
        s = sb.table("contacts_master").select("*", count="exact").eq("lead_source", "google_places").eq("status", status).execute()
        f.write(f"  status='{status}': {s.count}\n")

print("Written to prospector_status.txt")
