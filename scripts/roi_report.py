import sys
import os
import datetime
from dotenv import load_dotenv

# Add root to sys.path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

from modules.database.supabase_client import get_supabase

load_dotenv()

def print_roi_report():
    print("\n📊 SOVEREIGN EMPIRE: ROI & PERFORMANCE REPORT")
    print("=" * 50)
    
    try:
        sb = get_supabase()
        if not sb:
            print("ERROR: Supabase connection failed.")
            return

        # 1. Total Outreach (Lifetime)
        total = sb.table("outbound_touches").select("id", count="exact").execute().count
        
        # 2. Last 24 Hours
        yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat()
        daily = sb.table("outbound_touches").select("id", count="exact").gte("ts", yesterday).execute().count
        
        # 3. Channel Breakdown (Last 7 Days)
        week = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat()
        channels = sb.table("outbound_touches").select("channel").gte("ts", week).execute().data
        
        sms_count = sum(1 for c in channels if c['channel'] == 'sms')
        email_count = sum(1 for c in channels if c['channel'] == 'email')
        call_count = sum(1 for c in channels if c['channel'] == 'call')

        print(f"📈 TOTAL OUTREACH:     {total}")
        print(f"📅 LAST 24 HOURS:      {daily}")
        print("-" * 50)
        print(f"📱 SMS DISPATCHES:     {sms_count}")
        print(f"📧 EMAIL DISPATCHES:   {email_count}")
        print(f"📞 CALL ATTEMPTS:      {call_count}")
        print("-" * 50)
        
        # 4. Status Check
        campaign = sb.table("system_state").select("status").eq("key", "campaign_mode").single().execute()
        mode = campaign.data.get('status') if campaign.data else "UNKNOWN"
        print(f"⚙️  CAMPAIGN MODE:      {mode.upper()}")

    except Exception as e:
        print(f"❌ Metrics Retrieval Failed: {e}")

    print("=" * 50)
    print("System status: AUTONOMOUS & HARDENED")

if __name__ == "__main__":
    print_roi_report()
