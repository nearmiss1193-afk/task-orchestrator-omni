"""Phase 3 Verification — Simple and reliable"""
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone, timedelta
load_dotenv()
s = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

print("=" * 50)
print("PHASE 3 VERIFICATION")
print("=" * 50)

# 1. Latest email touches
print("\n--- 1. Latest 10 Email Touches ---")
touches = s.table("outbound_touches").select("ts,company,variant_id,variant_name,correlation_id,status").eq("channel", "email").order("ts", desc=True).limit(10).execute()
for t in touches.data:
    ts = str(t.get('ts') or '?')[:16]
    co = str(t.get('company') or '?')[:20]
    vid = str(t.get('variant_id') or '-')
    vn = str(t.get('variant_name') or '-')[:30]
    cid = str(t.get('correlation_id') or '-')[:15]
    print(f"  {ts} | {co} | V{vid}: {vn} | ID: {cid}")

# 2. A/B distribution
print("\n--- 2. A/B Variant Distribution ---")
all_t = s.table("outbound_touches").select("variant_id").eq("channel", "email").execute()
counts = {}
for t in all_t.data:
    v = str(t.get('variant_id') or 'pre-AB')
    counts[v] = counts.get(v, 0) + 1
for v in sorted(counts.keys(), key=str):
    print(f"  Variant {v}: {counts[v]} emails")

# 3. Email opens
print("\n--- 3. Email Opens (Pixel Tracking) ---")
try:
    opens = s.table("email_opens").select("opened_at,recipient_email,business_name").order("opened_at", desc=True).limit(5).execute()
    print(f"  Total tracked opens: {len(opens.data)}")
    for o in opens.data:
        print(f"  {str(o.get('opened_at') or '?')[:16]} | {o.get('recipient_email', '?')} | {o.get('business_name', '?')}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Today's activity
print("\n--- 4. Today's Activity ---")
today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
today_count = s.table("outbound_touches").select("id", count="exact").gt("ts", today).execute()
print(f"  Emails today: {today_count.count}")

# 5. GHL status
print("\n--- 5. GHL ID Status ---")
all_leads = s.table("contacts_master").select("ghl_contact_id").execute()
real = sum(1 for l in all_leads.data if l.get('ghl_contact_id') and not str(l['ghl_contact_id']).startswith('SCRAPED_'))
scraped = sum(1 for l in all_leads.data if str(l.get('ghl_contact_id') or '').startswith('SCRAPED_'))
print(f"  Real GHL IDs: {real} (SMS eligible)")
print(f"  SCRAPED_ IDs: {scraped} (need enrichment)")
print(f"  Total: {len(all_leads.data)}")

print("\n" + "=" * 50)
