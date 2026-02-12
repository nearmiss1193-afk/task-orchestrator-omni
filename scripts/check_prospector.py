"""Quick check if the prospector has been triggered by the heartbeat."""
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

# 1. Prospector triggered?
r = sb.table('system_state').select('*').eq('key', 'prospector_last_run').execute()
print('== prospector_last_run ==')
if r.data:
    for row in r.data:
        print(f"  TRIGGERED: value={row.get('value','')} status={row.get('status','')}")
else:
    print('  NOT SET YET (heartbeat has not fired or prospector not triggered)')

# 2. Cycle index set?
r2 = sb.table('system_state').select('*').eq('key', 'prospector_cycle_index').execute()
print('\n== cycle_index ==')
if r2.data:
    for row in r2.data:
        print(f"  value={row.get('value','')}")
else:
    print('  NOT SET (prospector has not completed a run)')

# 3. Any new leads from prospector?
try:
    r3 = sb.table('contacts_master').select('business_name, source, status, email', count='exact').eq('source', 'google_places').execute()
    count_gp = r3.count or 0
    print(f"\n== Leads with source=google_places: {count_gp} ==")
    for row in (r3.data or [])[:5]:
        email = (row.get('email') or 'none')[:30]
        print(f"  {row.get('business_name', '?')} | email={email}")
except Exception as e:
    print(f"\n== Leads check error: {e}")

# 4. Also check source=prospector
try:
    r4 = sb.table('contacts_master').select('business_name, source, status, email', count='exact').eq('source', 'prospector').execute()
    count_p = r4.count or 0
    print(f"\n== Leads with source=prospector: {count_p} ==")
except Exception as e:
    print(f"\n== source=prospector check error: {e}")

# 5. Total contactable leads
try:
    r5 = sb.table('contacts_master').select('id', count='exact').in_('status', ['new', 'research_done']).execute()
    print(f"\n== Total contactable (new+research_done): {r5.count} ==")
except Exception as e:
    print(f"\n== contactable check: {e}")

print('\nDone.')
