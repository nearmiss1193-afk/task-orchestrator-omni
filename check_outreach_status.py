import os
import sys
from datetime import datetime, timezone
import dateutil.parser
from dotenv import load_dotenv
from supabase import create_client

# Load env
sys.path.append(os.getcwd())
load_dotenv('.env.local')

def check_recent_outreach():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: Supabase credentials missing.")
        return

    supabase = create_client(url, key)
    
    print("\n🔍 Checking 'contacts_master' for recent outreach...")
    
    try:
        # Get last 10 contacts with outreach
        res = supabase.table("contacts_master")\
            .select("first_name, last_name, status, last_outreach_at, phone")\
            .neq("last_outreach_at", None)\
            .order("last_outreach_at", desc=True)\
            .limit(10)\
            .execute()
            
        contacts = res.data or []
        
        if not contacts:
            print("⚠️ No outreach records found.")
            return

        today_count = 0
        now_utc = datetime.now(timezone.utc).date()
        
        print(f"\nRecent Outreach Activity (Last 10):")
        print("-" * 60)
        print(f"{'Time':<25} | {'Name':<20} | {'Status':<15}")
        print("-" * 60)
        
        for c in contacts:
            ts_str = c.get('last_outreach_at')
            try:
                # Handle potentially different formats
                dt = dateutil.parser.parse(ts_str)
                # Check if today
                if dt.date() == datetime.now().date(): # Approximate local check
                     today_count += 1
                
                print(f"{ts_str:<25} | {c.get('first_name') or 'Unknown'} {c.get('last_name') or ''} | {c.get('status')}")
            except Exception as e:
                print(f"{ts_str:<25} | Error parsing date: {e}")

        print("-" * 60)
        if today_count > 0:
            print(f"✅ Found {today_count} outreach events matching today's date (local/UTC mix).")
        else:
            print("❄️ No outreach found with today's date.")

    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    check_recent_outreach()
