"""
Check actual outreach activity in the last 24 hours
"""
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone, timedelta

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

sb = create_client(url, key)

# Check last 24 hours of outreach
cutoff_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
cutoff_1h = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

print("="*60)
print("📊 OUTREACH ACTIVITY ANALYSIS")
print("="*60)

# Last 24 hours
result_24h = sb.table("outbound_touches").select("*", count="exact").gte("ts", cutoff_24h).execute()
print(f"\n✉️  Last 24 hours: {result_24h.count} messages")

# Last 1 hour
result_1h = sb.table("outbound_touches").select("*", count="exact").gte("ts", cutoff_1h).execute()
print(f"✉️  Last 1 hour: {result_1h.count} messages")

# Get latest outreach
latest = sb.table("outbound_touches").select("*").order("ts", desc=True).limit(5).execute()

if latest.data:
    print(f"\n📋 Latest outreach messages:")
    for msg in latest.data:
        print(f"   - {msg.get('ts')} | {msg.get('channel')} | Contact: {msg.get('contact_id')}")
else:
    print("\n⚠️  No outreach records found")

# Check contactable leads
contactable = sb.table("contacts_master").select("id,status,email,phone", count="exact").in_("status", ["new", "research_done"]).execute()
print(f"\n👥 Contactable leads: {contactable.count}")

if contactable.data:
    with_email = sum(1 for c in contactable.data if c.get('email'))
    with_phone = sum(1 for c in contactable.data if c.get('phone'))
    print(f"   - With email: {with_email}")
    print(f"   - With phone: {with_phone}")

print("\n" + "="*60)
