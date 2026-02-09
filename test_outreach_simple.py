"""
Test outreach logic - NO EMOJIS
"""
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
sb = create_client(url, key)

print("="*70)
print("AUTO_OUTREACH_LOOP SIMULATION")
print("="*70)

# Check current time
est = timezone(timedelta(hours=-5))
now_est = datetime.now(est)
is_sms_hours = 8 <= now_est.hour < 18 and now_est.weekday() < 6

print(f"\nCurrent time (EST): {now_est.strftime('%Y-%m-%d %H:%M:%S %A')}")
print(f"Hour: {now_est.hour}")
print(f"Weekday: {now_est.weekday()} (0=Monday, 6=Sunday)")
print(f"SMS hours active: {is_sms_hours}")

# Fetch contactable leads
print("\nFetching contactable leads (status IN new, research_done)...")
try:
    res = sb.table("contacts_master").select("id,full_name,email,phone,status").in_("status", ["new", "research_done"]).limit(10).execute()
    leads = res.data
    print(f"Found: {len(leads)} leads")
    
    if leads:
        print("\nLead details:")
        for i, lead in enumerate(leads, 1):
            print(f"\n{i}. {lead.get('full_name', 'Unknown')}")
            print(f"   ID: {lead.get('id')}")
            print(f"   Status: {lead.get('status')}")
            print(f"   Email: {lead.get('email', 'NONE')}")
            print(f"   Phone: {lead.get('phone', 'NONE')}")
            
            if lead.get('phone') and is_sms_hours:
                print(f"   Route: SMS (business hours)")
            elif lead.get('email'):
                print(f"   Route: EMAIL (24/7)")
            else:
                print(f"   Route: SKIP (no contact info)")
    else:
        print("WARNING: No leads with status 'new' or 'research_done'")
        
        # Check what statuses exist
        all_leads = sb.table("contacts_master").select("status", count="exact").execute()
        print(f"\nTotal leads in database: {all_leads.count}")
        
        # Get status breakdown
        from collections import Counter
        if all_leads.data:
            status_counts = Counter(l.get('status') for l in all_leads.data)
            print("\nStatus breakdown:")
            for status, count in status_counts.most_common():
                print(f"   {status}: {count}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
