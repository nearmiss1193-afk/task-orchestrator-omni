"""Check who outreach is ACTUALLY emailing"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# Get payloads from recent touches
r = sb.table('outbound_touches').select('payload,company,phone').order('ts', desc=True).limit(5).execute()
print("LAST 5 TOUCH PAYLOADS:")
for t in (r.data or []):
    payload = t.get('payload') or {}
    to_email = payload.get('to', '?')
    resend_id = payload.get('resend_email_id', '?')
    print(f"  TO: {to_email} | company: {t.get('company')} | resend: {resend_id}")

# Count total touches
r2 = sb.table('outbound_touches').select('id', count='exact').execute()
print(f"\nTotal outbound_touches: {r2.count}")

# Check: do any outreach_sent leads exist that ALSO appear in touches?
r3 = sb.table('contacts_master').select('id,full_name,email,phone').eq('status', 'outreach_sent').limit(5).execute()
print(f"\nSAMPLE 'outreach_sent' LEADS:")
for lead in (r3.data or []):
    print(f"  {lead.get('full_name')} | {lead.get('email')} | {lead.get('phone')}")
    # Check if this phone matches any outbound_touches
    phone = lead.get('phone')
    if phone:
        tr = sb.table('outbound_touches').select('ts,company', count='exact').eq('phone', phone).execute()
        print(f"    -> Touches found by phone: {tr.count}")
