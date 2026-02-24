import os, sys, json
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')

from supabase import create_client
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
sb = create_client(url, key)

# Check bucket
try:
    buckets = sb.storage.list_buckets()
    print('Buckets:', [b.name for b in buckets])
    
    if 'audit-pdfs' not in [b.name for b in buckets]:
        print("Creating 'audit-pdfs' bucket...")
        # create_bucket requires name, options
        sb.storage.create_bucket('audit-pdfs', {'public': True})
        print("Bucket created!")
except Exception as e:
    print('Bucket Error:', e)
    import traceback
    traceback.print_exc()

# Find a test lead with a website
res = sb.table('contacts_master').select('*').neq('website_url', '').in_('status', ['new', 'research_done']).limit(1).execute()
if not res.data:
    print('No test lead found')
    sys.exit(0)

lead = res.data[0]
print(f"Test lead: {lead.get('company_name')} ({lead.get('website_url')})")

try:
    from workers.audit_generator import generate_audit_for_lead
    print("Testing generate_audit_for_lead...")
    audit = generate_audit_for_lead(lead)
    print("Audit Success:", audit.get("success"))
    if not audit.get("success"):
        print("Audit Error:", audit.get("error"))
except Exception as e:
    print("Exception running generator:", e)
    import traceback
    traceback.print_exc()
