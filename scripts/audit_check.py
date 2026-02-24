import os, sys
from dotenv import load_dotenv
sys.path.insert(0, '.')
load_dotenv('.env')
load_dotenv('.env.local')
from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

# 1. audit_reports table
try:
    ar = supabase.table('audit_reports').select('report_id', count='exact').limit(1).execute()
    print(f'audit_reports table: EXISTS ({ar.count} rows)')
except Exception as e:
    print(f'audit_reports table: MISSING - {e}')

# 2. audit-pdfs bucket
try:
    buckets = supabase.storage.list_buckets()
    names = [b.name for b in buckets]
    has_audit = 'audit-pdfs' in names
    print(f'audit-pdfs bucket: {"EXISTS" if has_audit else "MISSING"}')
    print(f'All buckets: {names}')
except Exception as e:
    print(f'Storage error: {e}')

# 3. RESEND_API_KEY
rk = os.getenv('RESEND_API_KEY')
print(f'RESEND_API_KEY: {"SET (" + rk[:10] + "...)" if rk else "MISSING"}')

# 4. Fresh leads with website
fresh_site = supabase.table('contacts_master').select('id', count='exact').in_('status', ['new','research_done']).neq('website_url','').execute()
print(f'Fresh leads with website: {fresh_site.count}')

# 5. Stuck in audit_processing
stuck = supabase.table('contacts_master').select('id', count='exact').eq('status', 'audit_processing').execute()
print(f'Stuck in audit_processing: {stuck.count}')

# 6. Check Modal env - does it have RESEND_API_KEY?
print(f'\nGoogle API Key: {"SET" if os.getenv("GOOGLE_API_KEY") else "MISSING"}')
print(f'PageSpeed uses Google API: No key needed for basic use')
