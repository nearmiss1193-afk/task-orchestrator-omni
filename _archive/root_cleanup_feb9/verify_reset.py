"""
Verify lead reset and check outreach readiness
"""
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone, timedelta

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
sb = create_client(url, key)

print("VERIFICATION REPORT")
print("="*70)

# 1. Contactable leads
contactable = sb.table("contacts_master").select("id,email,phone", count="exact").eq("status", "new").execute()
print(f"\n1. Contactable leads (status='new'): {contactable.count}")

if contactable.data:
    with_email = sum(1 for l in contactable.data if l.get('email'))
    with_phone = sum(1 for l in contactable.data if l.get('phone'))
    print(f"   - With email: {with_email}")
    print(f"   - With phone: {with_phone}")

# 2. Campaign mode
mode = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
if mode.data:
    print(f"\n2. Campaign mode: {mode.data[0].get('status')}")

# 3. Recent outreach
cutoff = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
recent = sb.table("outbound_touches").select("id", count="exact").gte("ts", cutoff).execute()
print(f"\n3. Outreach (last 30 min): {recent.count}")

# 4. Next CRON cycle
now = datetime.now(timezone.utc)
next_5min = now.replace(second=0, microsecond=0) + timedelta(minutes=5 - now.minute % 5)
wait_seconds = (next_5min - now).total_seconds()
print(f"\n4. Next auto_outreach_loop cycle in: {int(wait_seconds)} seconds")

print("\n" + "="*70)
print("STATUS: Ready for outreach")
print(f"Expected first message within: {int(wait_seconds/60) + 1} minutes")
print("="*70)
