import os
import json
from supabase import create_client
from dotenv import load_dotenv

def verify_production_roi():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("❌ Supabase credentials missing")
        return

    sb = create_client(url, key)

    # 1. Check Campaign Mode
    state = sb.table("system_state").select("status").eq("key", "campaign_mode").single().execute()
    mode = state.data.get('status') if state.data else 'NOT_FOUND'
    print(f"--- ROI VERIFICATION REPORT ---")
    print(f"CAMPAIGN_MODE: {mode}")

    # 2. Check Recent Outreach
    touches = sb.table("outbound_touches").select("ts").order("ts", desc=True).limit(5).execute()
    print(f"RECENT_OUTREACH: {len(touches.data)} records found")
    for t in touches.data:
        print(f" - {t['ts']}")

    # 3. Check System Health Log
    health = sb.table("system_health_log").select("checked_at", "status").order("checked_at", desc=True).limit(3).execute()
    print(f"SYSTEM_HEARTBEATS: {len(health.data)} records found")
    for h in health.data:
        print(f" - {h['checked_at']}: {h['status']}")

if __name__ == "__main__":
    verify_production_roi()
