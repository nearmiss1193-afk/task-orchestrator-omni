"""
Direct query for lead status breakdown - ASCII only
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
sb = create_client(url, key)

# Get ALL leads with ALL fields
all_leads = sb.table("contacts_master").select("*").execute()

# Count by status
from collections import Counter
status_counts = Counter(l.get('status') for l in all_leads.data)

print("LEAD STATUS BREAKDOWN:")
print("="*50)
for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{status:30s} {count:5d}")

print("="*50)
print(f"TOTAL: {len(all_leads.data)}")

# Check contactable
contactable = [l for l in all_leads.data if l.get('status') in ['new', 'research_done']]
print(f"\nCONTACTABLE (new or research_done): {len(contactable)}")

# Check with contact info
with_email = sum(1 for l in all_leads.data if l.get('email'))
with_phone = sum(1 for l in all_leads.data if l.get('phone'))
print(f"Leads with email: {with_email}")
print(f"Leads with phone: {with_phone}")
