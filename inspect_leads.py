"""
Check leads table structure and get all leads
"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

sb = create_client(url, key)

print("="*60)
print("LEADS TABLE INSPECTION")
print("="*60)

# Get all leads
result = sb.table('leads').select('*').execute()
leads = result.data or []

print(f"\nTotal leads: {len(leads)}")

if leads:
    # Show all columns
    print(f"\nAll columns: {list(leads[0].keys())}")
    
    print("\n" + "-"*60)
    print("ALL LEADS:")
    print("-"*60)
    
    for lead in leads:
        print(f"\nID: {lead.get('id', '?')[:8]}...")
        print(f"   Company: {lead.get('company_name') or lead.get('full_name') or 'N/A'}")
        print(f"   Email: {lead.get('email', 'N/A')}")
        print(f"   Phone: {lead.get('phone', 'N/A')}")
        print(f"   Website: {lead.get('website_url', 'N/A')}")
        print(f"   Status: {lead.get('status', 'N/A')}")
        
        # Check for audit-related fields
        audit = lead.get('audit_link') or lead.get('audit_url') or lead.get('report_link')
        print(f"   Audit Link: {audit or 'NOT SET'}")

print("\n" + "="*60)
