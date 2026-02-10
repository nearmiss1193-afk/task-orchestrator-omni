"""Diagnose: do remaining NEW leads have website_url?"""
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
import os
from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
s = create_client(url, key)

new_leads = s.table('contacts_master').select(
    'id,company_name,website_url,email'
).in_('status', ['new', 'research_done']).limit(20).execute()

has_web = [l for l in new_leads.data if l.get('website_url')]
has_email = [l for l in new_leads.data if l.get('email')]
both = [l for l in new_leads.data if l.get('website_url') and l.get('email')]

print("New/research_done leads (sample): %d" % len(new_leads.data))
print("  With website_url: %d" % len(has_web))
print("  With email: %d" % len(has_email))
print("  Both (audit candidates): %d" % len(both))

print("\nFirst 5 with both:")
for l in both[:5]:
    cn = l.get('company_name') or '?'
    wu = l.get('website_url') or '?'
    em = l.get('email') or '?'
    print("  %s | %s | %s" % (cn, wu, em))

print("\nFirst 5 WITHOUT website:")
no_web = [l for l in new_leads.data if not l.get('website_url') and l.get('email')]
for l in no_web[:5]:
    cn = l.get('company_name') or '?'
    em = l.get('email') or '?'
    print("  %s | email: %s | NO WEBSITE" % (cn, em))

# Latest 8 touches
print("\nLatest 8 touches:")
latest = s.table('outbound_touches').select('ts,variant_id,company,variant_name').order('ts', desc=True).limit(8).execute()
for r in latest.data:
    vid = r.get('variant_id') or '?'
    cn = r.get('company') or '?'
    vn = r.get('variant_name') or '?'
    print("  %s | %s | %s | %s" % (str(r.get('ts','?'))[:22], vid[:6], cn[:30], vn[:40]))
