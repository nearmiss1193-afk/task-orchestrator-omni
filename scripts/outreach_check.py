import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY'))

# 1. Outreach last 30 min
r1 = sb.table('outbound_touches').select('*', count='exact').gte('ts', '2026-02-11T17:28:00').execute()
print(f"OUTREACH (last 30 min): {r1.count}")

# 2. Outreach today
r2 = sb.table('outbound_touches').select('*', count='exact').gte('ts', '2026-02-11T00:00:00').execute()
print(f"OUTREACH (today): {r2.count}")

# 3. Last 5 outreach entries
r3 = sb.table('outbound_touches').select('ts,channel,lead_id').order('ts', desc=True).limit(5).execute()
if r3.data:
    for t in r3.data:
        ts = t.get("ts", "?")
        ch = t.get("channel", "?")
        lid = str(t.get("lead_id", "?"))[:20]
        print(f"  Last: {ts} | {ch} | {lid}")
else:
    print("  NO OUTREACH ROWS")

# 4. Campaign mode
r4 = sb.table('system_state').select('*').eq('key', 'campaign_mode').execute()
if r4.data:
    print(f"CAMPAIGN MODE: {r4.data[0]}")
else:
    print("CAMPAIGN MODE: NOT SET")

# 5. Heartbeat
r5 = sb.table('system_health_log').select('checked_at,status').order('checked_at', desc=True).limit(3).execute()
if r5.data:
    for h in r5.data:
        print(f"HEARTBEAT: {h['checked_at']} | {h['status']}")
else:
    print("HEARTBEAT: NO ENTRIES")

# 6. Contactable leads
r6 = sb.table('contacts_master').select('status', count='exact').in_('status', ['new', 'research_done']).execute()
print(f"CONTACTABLE LEADS: {r6.count}")

# 7. Leads with contact info
r7 = sb.table('contacts_master').select('email,phone', count='exact').in_('status', ['new', 'research_done']).not_.is_('email', 'null').execute()
print(f"LEADS WITH EMAIL: {r7.count}")
