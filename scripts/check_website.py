import os
from supabase import create_client

sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# Check website_url coverage
r1 = sb.table('contacts_master').select('id', count='exact').neq('website_url','').not_.is_('website_url','null').execute()
r2 = sb.table('contacts_master').select('id', count='exact').in_('status',['new','research_done']).execute()
r3 = sb.table('contacts_master').select('id', count='exact').in_('status',['new','research_done']).neq('website_url','').not_.is_('website_url','null').execute()

print(f'Total leads with website_url: {r1.count}')
print(f'Contactable leads (new/research_done): {r2.count}')
print(f'Contactable WITH website_url: {r3.count}')
print(f'Contactable WITHOUT website_url: {r2.count - r3.count}')

# Sample some without website
r5 = sb.table('contacts_master').select('id,full_name,email,phone,company_name,niche,source,website_url').in_('status',['new','research_done']).limit(15).execute()
print('\nSample contactable leads:')
for l in r5.data:
    has_web = 'YES' if l.get('website_url') else 'NO'
    print(f'  {l["full_name"][:35]:35s} | web={has_web:3s} | src={l.get("source","")[:15]:15s} | niche={l.get("niche","")[:12]}')
