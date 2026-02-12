"""Full system verification — 6-point check per Antigravity v5.0 protocol."""
from supabase import create_client
import os, json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
now = datetime.now(timezone.utc)

print("=" * 60)
print("SYSTEM VERIFICATION — Feb 11, 2026")
print("=" * 60)

# 1. Outreach in last 30 min
cutoff_30 = (now - timedelta(minutes=30)).isoformat()
r = sb.table("outbound_touches").select("id", count="exact").gte("ts", cutoff_30).execute()
outreach_30 = r.count if r.count is not None else len(r.data)
print(f"\n[1] Outreach (30 min): {outreach_30} touches")

# 2. Heartbeat
r = sb.table("system_health_log").select("checked_at,status").order("checked_at", desc=True).limit(3).execute()
if r.data:
    last_hb = r.data[0].get("checked_at", "")[:19]
    hb_status = r.data[0].get("status", "?")
    print(f"[2] Last heartbeat: {last_hb} (status: {hb_status})")
else:
    print(f"[2] Last heartbeat: NONE")

# 3. Campaign mode
r = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
mode = r.data[0].get("status") if r.data else "unknown"
print(f"[3] Campaign mode: {mode}")

# 4. Contactable leads
r = sb.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).execute()
pool = r.count if r.count is not None else len(r.data)
print(f"[4] Contactable leads (new/research_done): {pool}")

# 5. Total leads
r = sb.table("contacts_master").select("id", count="exact").execute()
total = r.count if r.count is not None else len(r.data)
print(f"[5] Total leads: {total}")

# 6. Google Places leads (prospector)
r = sb.table("contacts_master").select("id", count="exact").eq("lead_source", "google_places").execute()
gp_count = r.count if r.count is not None else len(r.data)
print(f"[6] Google Places leads: {gp_count}")

# 7. Prospector last run
r = sb.table("system_state").select("status").eq("key", "prospector_last_run").execute()
if r.data and r.data[0].get("status"):
    last_ts = datetime.fromisoformat(r.data[0]["status"])
    hours_ago = (now - last_ts).total_seconds() / 3600
    print(f"[7] Prospector last run: {hours_ago:.1f}h ago")
else:
    print(f"[7] Prospector last run: NEVER")

# 8. Cron count
import subprocess
r = subprocess.run(["python", "-c", "import re; text=open('deploy.py').read(); print(len(re.findall(r'schedule=modal\\.Cron', text)))"],
                   capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)) + "/..")
cron_count = r.stdout.strip()
print(f"[8] Modal CRONs: {cron_count}/4")

# Summary
print(f"\n{'=' * 60}")
checks_passed = 0
total_checks = 6

if outreach_30 > 0: checks_passed += 1; s1 = "PASS"
else: s1 = "WARN (0 in 30 min)"

if hb_status in ["ok", "working"]: checks_passed += 1; s2 = "PASS"
else: s2 = f"WARN ({hb_status})"

if mode == "working": checks_passed += 1; s3 = "PASS"
else: s3 = f"FAIL ({mode})"

if pool > 0: checks_passed += 1; s4 = "PASS"
else: s4 = "FAIL (empty)"

if gp_count > 0: checks_passed += 1; s5 = "PASS"
else: s5 = "FAIL (0)"

if cron_count and int(cron_count) <= 4: checks_passed += 1; s6 = "PASS"
else: s6 = f"WARN ({cron_count})"

print(f"RESULTS: {checks_passed}/{total_checks} passed")
print(f"  [1] Outreach active:     {s1}")
print(f"  [2] Heartbeat alive:     {s2}")
print(f"  [3] Campaign mode:       {s3}")
print(f"  [4] Lead pool:           {s4}")
print(f"  [5] Prospector working:  {s5}")
print(f"  [6] Cron count safe:     {s6}")
print(f"{'=' * 60}")
