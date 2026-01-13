"""Full DB status check"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

sb = create_client(url, key)

print("="*60)
print("DATABASE STATUS")
print("="*60)

# Leads table
print("\n📊 LEADS TABLE:")
leads = sb.table('leads').select('*').execute()
total = len(leads.data) if leads.data else 0
print(f"   Total: {total}")

if leads.data:
    # Show columns
    print(f"   Columns: {list(leads.data[0].keys())}")
    
    # Count by status
    statuses = {}
    for l in leads.data:
        s = l.get('status', 'unknown')
        statuses[s] = statuses.get(s, 0) + 1
    print(f"   By status: {statuses}")
    
    # Count with audit links
    with_audit = len([l for l in leads.data if l.get('audit_link')])
    print(f"   With audit_link: {with_audit}")
    
    # Show all leads
    print("\n   All leads:")
    for l in leads.data:
        print(f"     - {l.get('company_name', '?')[:30]} | {l.get('email', 'N/A')[:25]} | status: {l.get('status', '?')} | audit: {'YES' if l.get('audit_link') else 'NO'}")

# Contacts master table
print("\n📊 CONTACTS_MASTER TABLE:")
try:
    contacts = sb.table('contacts_master').select('*').execute()
    total = len(contacts.data) if contacts.data else 0
    print(f"   Total: {total}")
    if contacts.data and total > 0:
        print(f"   Columns: {list(contacts.data[0].keys())}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
