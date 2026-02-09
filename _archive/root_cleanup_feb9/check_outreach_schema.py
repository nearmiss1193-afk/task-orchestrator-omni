"""
Check outbound_touches table schema and recent data
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

sb = create_client(url, key)

print("="*70)
print("📊 OUTBOUND_TOUCHES TABLE ANALYSIS")
print("="*70)

# Get recent outreach
result = sb.table("outbound_touches").select("*").order("ts", desc=True).limit(10).execute()

print(f"\nTotal records found: {len(result.data) if result.data else 0}")

if result.data:
    print("\n📧 Last 10 outreach records:")
    for i, record in enumerate(result.data, 1):
        print(f"\n{i}. Timestamp: {record.get('ts')}")
        print(f"   Keys: {list(record.keys())}")
        print(f"   Data: {record}")
else:
    print("\n⚠️  No outreach records found!")

# Check lead statuses
leads = sb.table("contacts_master").select("status", count="exact").execute()
print(f"\n\n👥 Total leads in database: {leads.count}")

# Group by status
from collections import Counter
if leads.data:
    status_counts = Counter(l.get('status') for l in leads.data)
    print("\nLead status breakdown:")
    for status, count in status_counts.most_common():
        print(f"   {status}: {count}")

print("\n" + "="*70)
