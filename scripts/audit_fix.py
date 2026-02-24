import os, sys, json
from dotenv import load_dotenv
sys.path.insert(0, '.')
load_dotenv('.env')
load_dotenv('.env.local')
from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

results = {}

# 1. audit_reports
try:
    ar = supabase.table('audit_reports').select('report_id', count='exact').limit(1).execute()
    results['audit_reports_table'] = f'EXISTS ({ar.count} rows)'
except Exception as e:
    results['audit_reports_table'] = f'MISSING: {e}'

# 2. buckets
try:
    buckets = supabase.storage.list_buckets()
    names = [b.name for b in buckets]
    results['storage_buckets'] = names
    results['audit_pdfs_bucket'] = 'audit-pdfs' in names
except Exception as e:
    results['storage_error'] = str(e)

# 3. envs
results['RESEND_API_KEY'] = 'SET' if os.getenv('RESEND_API_KEY') else 'MISSING'
results['GOOGLE_API_KEY'] = 'SET' if os.getenv('GOOGLE_API_KEY') else 'MISSING'

# 4. stuck leads
stuck = supabase.table('contacts_master').select('id', count='exact').eq('status', 'audit_processing').execute()
results['stuck_audit_processing'] = stuck.count

# 5. fresh with website
fs = supabase.table('contacts_master').select('id', count='exact').in_('status', ['new','research_done']).neq('website_url','').execute()
results['fresh_with_website'] = fs.count

# 6. Fix stuck leads
if stuck.count and stuck.count > 0:
    supabase.table('contacts_master').update({'status': 'new'}).eq('status', 'audit_processing').execute()
    results['stuck_fixed'] = True

# 7. Create audit-pdfs bucket if missing
if not results.get('audit_pdfs_bucket', False):
    try:
        supabase.storage.create_bucket('audit-pdfs', {'public': True})
        results['bucket_created'] = True
    except Exception as e:
        results['bucket_create_error'] = str(e)

with open('audit_infra.json', 'w') as f:
    json.dump(results, f, indent=2)
print('Done.')
