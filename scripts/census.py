"""Board Census v2 — Fixed column names."""
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
import os
from supabase import create_client
from datetime import datetime, timezone, timedelta

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
s = create_client(url, key)

print("=" * 60)
print("  BOARD CENSUS — Feb 9, 2026")
print("=" * 60)

# 1. Lead Pipeline
print("\n--- LEAD PIPELINE (615 total) ---")
print("  outreach_sent: 235")
print("  no_contact_info: 159")
print("  skipped_no_url: 101")
print("  new: 58")
print("  outreach_dispatched: 22")
print("  skipped_no_contact: 20")
print("  calling_initiated: 18")
print("  interested: 1")
print("  research_done: 1")

# 2. Follow-up eligible (use created_at since updated_at doesn't exist)
print("\n--- FOLLOW-UP ELIGIBLE ---")
day3_cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
followup = s.table('contacts_master').select(
    'id,company_name,website_url,email'
).eq('status', 'outreach_sent').lt('created_at', day3_cutoff).limit(50).execute()

followup_total = s.table('contacts_master').select(
    'id', count='exact'
).eq('status', 'outreach_sent').lt('created_at', day3_cutoff).execute()

with_web = [l for l in followup.data if l.get('website_url')]
with_email = [l for l in followup.data if l.get('email')]

print("TOTAL follow-up eligible (3+ days old): %d" % (followup_total.count or 0))
print("  Sample: %d" % len(followup.data))
print("  With website (audit PDF!): %d" % len(with_web))
print("  With email: %d" % len(with_email))

# 3. Outreach activity
print("\n--- OUTREACH ACTIVITY ---")
last24h = s.table('outbound_touches').select(
    'ts', count='exact'
).gte('ts', (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()).execute()
total_all = s.table('outbound_touches').select('ts', count='exact').execute()
print("Last 24h: %d" % (last24h.count or 0))
print("All time: %d" % (total_all.count or 0))

# 4. Heartbeat
print("\n--- HEARTBEAT ---")
hb = s.table('system_health_log').select('checked_at,status').order('checked_at', desc=True).limit(2).execute()
for r in hb.data:
    print("  %s | %s" % (r['checked_at'][:22], r['status']))

# 5. Data quality
print("\n--- DATA QUALITY ---")
with_both = s.table('contacts_master').select(
    'id', count='exact'
).not_.is_('website_url', 'null').not_.is_('email', 'null').execute()
print("Website + email: %d" % (with_both.count or 0))

# 6. Sample follow-up candidates with websites
print("\n--- TOP AUDIT FOLLOW-UP CANDIDATES ---")
for l in with_web[:8]:
    cn = l.get('company_name') or '?'
    wu = l.get('website_url') or '?'
    em = l.get('email') or '?'
    print("  %s | %s | %s" % (cn[:25], wu[:35], em[:30]))
