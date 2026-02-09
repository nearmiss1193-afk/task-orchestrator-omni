import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone, timedelta

load_dotenv()
s = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])
now = datetime.now(timezone.utc)

fresh = s.table('contacts_master').select('id', count='exact').in_('status', ['new', 'research_done']).execute()
cm = s.table('system_state').select('status').eq('key', 'campaign_mode').execute()
hb = s.table('system_health_log').select('checked_at').order('checked_at', desc=True).limit(1).execute()
ot = s.table('outbound_touches').select('id', count='exact').gte('ts', (now - timedelta(minutes=30)).isoformat()).execute()

mode = cm.data[0]['status'] if cm.data else '??'
last_hb = hb.data[0]['checked_at'] if hb.data else '??'

print(f"Fresh leads: {fresh.count}")
print(f"Campaign: {mode}")
print(f"Heartbeat: {last_hb}")
print(f"Outreach 30min: {ot.count}")

# SMS channel check
sms_ever = s.table('outbound_touches').select('id', count='exact').eq('channel', 'sms').execute()
print(f"SMS all-time: {sms_ever.count}")

if ot.count > 0:
    print("STATUS: ALL SYSTEMS GO")
else:
    print("STATUS: VERIFICATION PENDING - wait 5 min for CRON")
