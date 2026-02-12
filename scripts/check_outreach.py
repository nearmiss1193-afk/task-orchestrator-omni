"""Check outreach status - database truth"""
import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(url, key)

# 1. Recent outreach
print('=== OUTREACH (last 24h) ===')
r = sb.table('outbound_touches').select('*', count='exact').gte('ts', '2026-02-10T13:00:00').order('ts', desc=True).limit(5).execute()
print(f'Count last 24h: {r.count}')
if r.data:
    for t in r.data:
        ts = str(t.get('ts', '?'))[:19]
        ch = t.get('channel', '?')
        cid = str(t.get('contact_id', '?'))[:16]
        st = t.get('status', '?')
        print(f'  {ts} | {ch} | {cid} | {st}')
else:
    print('  NO outreach in last 24h')

# 2. Campaign mode
print('\n=== CAMPAIGN MODE ===')
r2 = sb.table('system_state').select('*').eq('key', 'campaign_mode').execute()
if r2.data:
    print(f'  Status: {r2.data[0].get("status", "?")}')
else:
    print('  NOT SET')

# 3. Contactable leads
print('\n=== CONTACTABLE LEADS ===')
r3 = sb.table('contacts_master').select('status', count='exact').in_('status', ['new', 'research_done']).execute()
print(f'  Contactable: {r3.count}')

r3b = sb.table('contacts_master').select('status').execute()
status_counts = {}
for row in r3b.data:
    s = row.get('status', 'unknown')
    status_counts[s] = status_counts.get(s, 0) + 1
for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
    print(f'    {s}: {c}')

# 4. Heartbeat
print('\n=== HEARTBEAT ===')
r4 = sb.table('system_health_log').select('checked_at,status').order('checked_at', desc=True).limit(3).execute()
if r4.data:
    for h in r4.data:
        ca = str(h.get('checked_at', '?'))[:19]
        st = h.get('status', '?')
        print(f'  {ca} | {st}')
else:
    print('  No heartbeats')

# 5. Leads with contact info
print('\n=== LEADS WITH CONTACT INFO ===')
r5 = sb.table('contacts_master').select('id,email,phone', count='exact').in_('status', ['new', 'research_done']).execute()
has_email = sum(1 for r in r5.data if r.get('email'))
has_phone = sum(1 for r in r5.data if r.get('phone'))
print(f'  Total contactable: {r5.count}')
print(f'  Has email: {has_email}')
print(f'  Has phone: {has_phone}')
