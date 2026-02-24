import os, sys, json
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')

from supabase import create_client
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
sb = create_client(url, key)

res = sb.table('contacts_master').select('*').neq('website_url', '').neq('email', '').in_('status', ['new', 'research_done']).limit(1).execute()
if not res.data:
    print('No test lead')
    sys.exit(0)
lead = res.data[0]

with open('audit_error.txt', 'w', encoding='utf-8') as f:
    f.write(f"Testing lead: {lead.get('company_name')} ({lead.get('website_url')}) | Email: {lead.get('email')}\n")
    try:
        from workers.audit_generator import generate_audit_for_lead
        audit = generate_audit_for_lead(lead)
        if not audit.get("success"):
            f.write(f"EXACT_ERROR_MSG:: {audit.get('error')}\n")
        else:
            f.write(f"SUCCESS! PDF Size: {len(audit.get('pdf_b64', ''))}\n")
            f.write(f"Details: {json.dumps(audit.get('audit_results', {}))}\n")
    except Exception as e:
        import traceback
        f.write(f"EXACT_EXCEPTION_MSG:: {str(e)}\n\n")
        f.write(traceback.format_exc())
print("Saved to audit_error.txt")
