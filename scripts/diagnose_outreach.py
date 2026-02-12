"""Quick diagnosis: why is outreach at 0?"""
from supabase import create_client
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
now = datetime.now(timezone.utc)

print("=== LEAD STATUS BREAKDOWN ===")
for status in ["new", "research_done", "outreach_sent", "sequence_complete", "responded", "customer", "contacted"]:
    r = sb.table("contacts_master").select("id", count="exact").eq("status", status).execute()
    ct = r.count if r.count is not None else len(r.data)
    if ct > 0:
        print("  %s: %d" % (status, ct))

r = sb.table("contacts_master").select("id", count="exact").execute()
print("  TOTAL: %s" % r.count)

print("\n=== LAST 5 OUTREACH TOUCHES ===")
r = sb.table("outbound_touches").select("ts,channel,lead_id").order("ts", desc=True).limit(5).execute()
for d in r.data:
    ts = d.get("ts", "?")[:19]
    ch = d.get("channel", "?")
    lid = str(d.get("lead_id", "?"))[:12]
    print("  %s | %s | lead:%s" % (ts, ch, lid))

today_start = now.replace(hour=0, minute=0, second=0).isoformat()
r = sb.table("outbound_touches").select("id", count="exact").gte("ts", today_start).execute()
print("  Today total: %s" % r.count)

print("\n=== WHY OUTREACH MIGHT BE 0 ===")
# Check: any leads with email + status new?
r = sb.table("contacts_master").select("id,email,status,company_name").in_("status", ["new", "research_done"]).limit(10).execute()
print("Contactable leads (new/research_done):")
for d in r.data:
    email = d.get("email", "none")
    print("  id:%s | %s | email:%s | status:%s" % (str(d["id"])[:8], d.get("company_name", "?"), email, d.get("status", "?")))

if len(r.data) == 0:
    print("  >>> ZERO contactable leads! Pool is EMPTY.")
    print("  >>> Outreach cannot send because there are no leads to contact.")
    print("  >>> Fix: Run prospector manually OR recycle old leads.")

# Check recycling candidates (outreach_sent > 3 days ago)
cutoff_3d = (now - timedelta(days=3)).isoformat()
r = sb.table("contacts_master").select("id", count="exact").eq("status", "outreach_sent").execute()
print("\n  Leads with 'outreach_sent' status: %s (recyclable after 3-day cooldown)" % r.count)

r = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
print("  Campaign mode: %s" % (r.data[0]["status"] if r.data else "unknown"))
