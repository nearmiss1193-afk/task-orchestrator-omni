import os
import sys
from datetime import datetime, timedelta, timezone

# Add current dir to path
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

try:
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    
    if not supabase:
        print("❌ Supabase client initialization failed.")
        sys.exit(1)
        
    print("📡 Querying Outbound Touches (Last 14 Days)...")
    
    # Check total count
    res_total = supabase.table("outbound_touches").select("id", count="exact").execute()
    print(f"Total Touches: {res_total.count}")
    
    # Check last 14 days by date
    res_recent = supabase.table("outbound_touches").select("ts, channel").order("ts", desc=True).limit(50).execute()
    
    if not res_recent.data:
        print("📭 No outreach found in last 50 records.")
    # Check for Truth Payload
    print("\n🔍 Searching for Truth Payloads (v5.6):")
    res_truth = supabase.table("outbound_touches").select("ts, details").ilike("details->>mode", "truth_verification").order("ts", desc=True).limit(5).execute()
    
    if res_truth.data:
        for row in res_truth.data:
            print(f"✅ FOUND: {row['ts']} | {row['details']}")
    else:
        print("❌ NO TRUTH PAYLOADS FOUND. Outreach may still be blocked.")
        
except Exception as e:
    print(f"❌ Error: {e}")
