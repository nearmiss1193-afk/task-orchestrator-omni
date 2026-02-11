"""Quick health check on the outreach system"""
import os
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
from supabase import create_client

s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

# 1. Campaign mode - get all columns
cm = s.table('system_state').select('*').eq('key', 'campaign_mode').execute()
print('=== CAMPAIGN MODE ===')
for r in cm.data:
    print(f"  {r}")

# 2. Recent outreach (last 5)
try:
    ot = s.table('outbound_touches').select('*', count='exact').order('ts', desc=True).limit(5).execute()
    print(f'\n=== OUTBOUND TOUCHES (total={ot.count}) ===')
    for r in ot.data:
        cid = str(r.get('contact_id','?'))[:8]
        print(f"  {r.get('ts','?')} | {r.get('channel','?')} | {cid}...")
except Exception as e:
    print(f'\n=== OUTBOUND TOUCHES ERROR: {e} ===')

# 3. Heartbeat
try:
    hb = s.table('system_health_log').select('*').order('checked_at', desc=True).limit(3).execute()
    print('\n=== HEARTBEAT ===')
    for r in hb.data:
        print(f"  {r.get('checked_at','?')} | {r.get('status','?')}")
except Exception as e:
    print(f'\n=== HEARTBEAT ERROR: {e} ===')

# 4. Contacts
ct = s.table('contacts_master').select('id', count='exact').execute()
print(f'\n=== CONTACTS: {ct.count} total ===')

# Status breakdown
for status_val in ['new', 'research_done', 'contacted', 'responded', 'customer']:
    c = s.table('contacts_master').select('id', count='exact').eq('status', status_val).execute()
    if c.count and c.count > 0:
        print(f"  {status_val}: {c.count}")

# 5. Contacts with phone numbers (for call sheet)
has_phone = s.table('contacts_master').select('id', count='exact').neq('phone', '').execute()
print(f"\n=== CONTACTS WITH PHONE: {has_phone.count} ===")

has_email = s.table('contacts_master').select('id', count='exact').neq('email', '').execute()
print(f"=== CONTACTS WITH EMAIL: {has_email.count} ===")

has_website = s.table('contacts_master').select('id', count='exact').neq('website_url', '').execute()
print(f"=== CONTACTS WITH WEBSITE: {has_website.count} ===")
