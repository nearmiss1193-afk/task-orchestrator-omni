"""
Why aren't the 241 'new' leads being contacted?
Schema-safe version — discover columns first.
"""
import os, json
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.environ.get("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
key = os.environ.get("SUPABASE_KEY", "")
sb = create_client(url, key)

print("=" * 60)
print("WHY AREN'T NEW LEADS BEING CONTACTED?")
print("=" * 60)

# 1. New leads stats
r = sb.table("contacts_master").select("id,email,phone,total_touches").eq("status", "new").execute()
data = r.data or []
has_email = [d for d in data if d.get('email')]
has_phone = [d for d in data if d.get('phone')]
zero_touch = [d for d in data if (d.get('total_touches') or 0) == 0]
print(f"\n1. 'NEW' LEADS:")
print(f"   Total: {len(data)}")
print(f"   Has email: {len(has_email)}")
print(f"   Has phone: {len(has_phone)}")
print(f"   0 touches: {len(zero_touch)}")

# 2. Outbound touches schema
r2 = sb.table("outbound_touches").select("*").order("ts", desc=True).limit(1).execute()
if r2.data:
    print(f"\n2. OUTBOUND_TOUCHES SCHEMA:")
    for k in sorted(r2.data[0].keys()):
        print(f"   {k}")

# 3. Last 10 touches (safe columns only)
r3 = sb.table("outbound_touches").select("*").order("ts", desc=True).limit(10).execute()
print(f"\n3. LAST 10 TOUCHES:")
for t in (r3.data or []):
    ts = t.get('ts', '?')
    channel = t.get('channel', '?')
    contact = t.get('contact_id', t.get('lead_id', '?'))
    status = t.get('status', t.get('result', '?'))
    print(f"   {ts} | {channel} | {status} | contact: {str(contact)[:30]}")

# 4. System state
r4 = sb.table("system_state").select("*").execute()
print(f"\n4. SYSTEM STATE:")
for row in (r4.data or []):
    k = row.get('key', '?')
    s = row.get('status', row.get('value', '?'))
    print(f"   {k}: {s}")

# 5. Last heartbeat
r5 = sb.table("system_health_log").select("checked_at,status").order("checked_at", desc=True).limit(3).execute()
print(f"\n5. LAST HEARTBEATS:")
for h in (r5.data or []):
    print(f"   {h.get('checked_at')} | {h.get('status')}")

print(f"\n{'=' * 60}")
