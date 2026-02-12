import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY'))

# Last 5 outreach
r3 = sb.table('outbound_touches').select('*').order('ts', desc=True).limit(5).execute()
if r3.data:
    print("LAST 5 OUTREACH:")
    for t in r3.data:
        print("  " + str(t.get("ts","?")) + " | " + str(t.get("channel","?")) + " | " + str(t.get("status","?")))
else:
    print("NO OUTREACH ROWS AT ALL")

# Campaign mode
r4 = sb.table('system_state').select('*').eq('key', 'campaign_mode').execute()
if r4.data:
    print("CAMPAIGN MODE: " + str(r4.data[0].get("status", r4.data[0].get("value", "?"))))
else:
    print("CAMPAIGN MODE: NOT SET")

# Heartbeat
r5 = sb.table('system_health_log').select('checked_at,status').order('checked_at', desc=True).limit(3).execute()
if r5.data:
    print("HEARTBEAT:")
    for h in r5.data:
        print("  " + str(h["checked_at"]) + " | " + str(h["status"]))
else:
    print("HEARTBEAT: NO ENTRIES")

# Contactable leads
r6 = sb.table('contacts_master').select('*', count='exact').in_('status', ['new', 'research_done']).execute()
print("CONTACTABLE LEADS: " + str(r6.count))
