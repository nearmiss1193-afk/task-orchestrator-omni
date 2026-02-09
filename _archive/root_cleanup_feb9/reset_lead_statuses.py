"""
Reset lead statuses to restart outreach
Per Master Prompt Section 1: Database results are truth
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
sb = create_client(url, key)

print("="*70)
print("LEAD STATUS RESET - RESTARTING OUTREACH")
print("="*70)

# Check current status distribution
print("\nCurrent status distribution:")
all_leads = sb.table("contacts_master").select("status").execute()
from collections import Counter
status_counts = Counter(l.get('status') for l in all_leads.data)
for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {status}: {count}")

# Reset leads to 'new' status
print("\nResetting leads to 'new' status...")
print("Targeting statuses: outreach_sent, outreach_dispatched, contacted, failed")

result = sb.table("contacts_master").update({"status": "new"}).in_(
    "status", ["outreach_sent", "outreach_dispatched", "contacted", "failed", "no_contact_info"]
).execute()

print(f"\nReset {len(result.data)} leads to 'new' status")

# Verify
new_count = sb.table("contacts_master").select("id", count="exact").eq("status", "new").execute()
print(f"Contactable leads (status='new'): {new_count.count}")

# Set campaign mode to working
sb.table("system_state").upsert({
    "key": "campaign_mode",
    "status": "working",
    "updated_at": "NOW()"
}, on_conflict="key").execute()

print("\nCampaign mode set to 'working'")
print("\nOutreach will resume within 5 minutes (next CRON cycle)")
print("="*70)
