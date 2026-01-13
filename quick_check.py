from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

print(f"URL: {url[:30] if url else 'MISSING'}...")
print(f"KEY: {key[:20] if key else 'MISSING'}...")

if not url or not key:
    print("ERROR: Missing Supabase credentials")
    exit(1)

supabase = create_client(url, key)
leads = supabase.table('leads').select('*').execute()

total = len(leads.data) if leads.data else 0
print(f"\nTotal leads in DB: {total}")

if leads.data:
    print("\nLast 5 prospects:")
    for l in leads.data[-5:]:
        name = l.get('company_name', '?')[:35]
        email = l.get('email', 'N/A')
        has_audit = 'READY' if l.get('audit_link') else 'PENDING'
        print(f"  [{has_audit}] {name} | {email}")
