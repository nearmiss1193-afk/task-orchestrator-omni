import os
from supabase import create_client
from dotenv import load_dotenv
from collections import Counter

load_dotenv(".env.local")

def check_campaigns():
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Supabase config missing. Cannot check campaigns.")
        return

    try:
        supabase = create_client(url, key)
        
        # Get all lead statuses
        # Note: If database is huge, pagination is needed. For <1000 leads, this is fine.
        res = supabase.table("contacts_master").select("status").execute()
        
        if not res.data:
            print("⚠️ No leads found in database.")
            return

        counts = Counter([r['status'] for r in res.data])
        
        print("\n📊 CAMPAIGN STATUS REPORT")
        print("="*30)
        print(f"Total Leads: {len(res.data)}")
        print("-" * 30)
        
        for status, count in counts.most_common():
            print(f"{status.ljust(20)}: {count}")
            
        print("="*30)
        
        # Check active campaign specifically
        active = counts.get('outreach_sent', 0) + counts.get('nurture_day_3', 0) + counts.get('nurture_day_10', 0)
        print(f"🔥 Active Campaigning: {active} leads")
        
        # Check queued
        ready = counts.get('research_done', 0)
        print(f"⏳ Ready for Outreach: {ready} leads")
        
        # Check new
        new = counts.get('new', 0)
        print(f"📥 New/Pending:       {new} leads")

    except Exception as e:
        print(f"❌ Error checking campaigns: {str(e)}")

if __name__ == "__main__":
    check_campaigns()
