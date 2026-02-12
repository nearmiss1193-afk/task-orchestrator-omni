"""Quick system status audit for Dan's briefing"""
import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client
from collections import Counter
from datetime import datetime, timezone, timedelta

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(url, key)

# 1. Lead pipeline
statuses = sb.table('contacts_master').select('status', count='exact').execute()
counts = Counter(r['status'] for r in statuses.data)
print('=== LEAD PIPELINE ===')
for s, c in sorted(counts.items(), key=lambda x: -x[1]):
    print(f'  {s}: {c}')
print(f'  TOTAL: {len(statuses.data)}')

# 2. Outreach
now = datetime.now(timezone.utc)
for label, days in [('7 days', 7), ('30 days', 30)]:
    cutoff = (now - timedelta(days=days)).isoformat()
    touches = sb.table('outbound_touches').select('channel,ts', count='exact').gte('ts', cutoff).execute()
    print(f'\n=== OUTREACH (Last {label}) ===')
    print(f'  Total touches: {touches.count}')
    if touches.data:
        ch_counts = Counter(r.get('channel') for r in touches.data)
        for ch, c in ch_counts.items():
            print(f'    {ch}: {c}')
        latest = max(r['ts'] for r in touches.data)
        print(f'  Latest: {latest}')

# 3. Campaign mode
state = sb.table('system_state').select('*').eq('key', 'campaign_mode').execute()
if state.data:
    print(f'\n=== CAMPAIGN MODE: {state.data[0].get("status", "unknown")} ===')

# 4. Heartbeat
hb = sb.table('system_health_log').select('checked_at,status').order('checked_at', desc=True).limit(5).execute()
print('\n=== HEARTBEAT (Last 5) ===')
for h in (hb.data or []):
    print(f'  {h["checked_at"]} - {h["status"]}')
if not hb.data:
    print('  NO HEARTBEATS')

# 5. Customers / conversions
customers = sb.table('contacts_master').select('id', count='exact').eq('status', 'customer').execute()
print(f'\n=== CONVERSIONS ===')
print(f'  Customers: {customers.count}')
