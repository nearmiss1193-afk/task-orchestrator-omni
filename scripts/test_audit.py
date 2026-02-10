"""Detailed test - show full audit output without PDF viewer."""
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
import os
from supabase import create_client
from workers.audit_generator import generate_audit_for_lead

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
s = create_client(url, key)

# Get 3 leads with websites to test variety
leads = s.table('contacts_master').select(
    'id,company_name,website_url,niche,email,full_name'
).not_.is_('website_url', 'null').not_.is_('email', 'null').eq('funnel_stage', 'new').limit(3).execute()

print(f"Testing {len(leads.data)} leads\n")

for i, lead in enumerate(leads.data):
    print(f"\n{'='*60}")
    print(f"  LEAD #{i+1}: {lead.get('company_name','?')} | {lead.get('website_url','?')}")
    print(f"{'='*60}")
    
    result = generate_audit_for_lead(lead)
    
    if result["success"]:
        ar = result["audit_results"]
        print(f"\n  RESULTS:")
        print(f"    PageSpeed: {ar['pagespeed'].get('score','N/A')}/100 ({ar['pagespeed']['status']})")
        print(f"    Privacy:   {ar['privacy']['status'].upper()} — {ar['privacy']['details']}")
        print(f"    AI Ready:  {ar['ai_readiness']['status'].upper()} — {ar['ai_readiness']['details']}")
        print(f"    Criticals: {ar['criticals']}")
        print(f"\n  EMAIL:")
        print(f"    Subject: {result['subject']}")
        print(f"    PDF: {result['pdf_filename']} ({len(result['pdf_b64'])} chars b64)")
        
        # Save first PDF for user inspection
        if i == 0:
            import base64
            pdf_bytes = base64.b64decode(result['pdf_b64'])
            with open('scripts/test_audit.pdf', 'wb') as f:
                f.write(pdf_bytes)
            print(f"\n  >> PDF saved to scripts/test_audit.pdf ({len(pdf_bytes)} bytes)")
    else:
        print(f"\n  FAILED: {result.get('error')}")

print(f"\n{'='*60}")
print("TESTS COMPLETE")
