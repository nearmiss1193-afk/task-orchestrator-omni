from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
import os
from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
s = create_client(url, key)

# Get ALL leads, only safe columns
all_leads = s.table('contacts_master').select(
    'company_name,website_url,niche,email,full_name'
).in_('funnel_stage', ['new', 'research_done']).limit(500).execute()

has_web = [r for r in all_leads.data if r.get('website_url')]
has_email = [r for r in all_leads.data if r.get('email')]
candidates = [r for r in all_leads.data if r.get('website_url') and r.get('email')]

print(f"Total queried: {len(all_leads.data)}")
print(f"Has website: {len(has_web)}")
print(f"Has email: {len(has_email)}")
print(f"Audit candidates (website + email): {len(candidates)}")

print("\n=== SAMPLE AUDIT CANDIDATES ===")
for r in candidates[:5]:
    print(f"  {r.get('company_name','?')} | {r.get('website_url','?')} | {r.get('niche','?')}")
    print(f"    email: {r.get('email','?')} | name: {r.get('full_name','?')}")
