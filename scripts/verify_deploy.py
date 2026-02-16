
import os
import json
from supabase import create_client
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

def verify_system_metrics():
    # Load .env for local script execution
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Error: Missing Supabase credentials")
        return

    sb = create_client(url, key)
    
    # 1. Heartbeat check (last 15 min)
    cutoff_hb = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
    hb = sb.table("system_health_log").select("checked_at", "status").gte("checked_at", cutoff_hb).order("checked_at", desc=True).limit(5).execute()
    
    print("\n--- HEARTBEATS (Last 15m) ---")
    if hb.data:
        for row in hb.data:
            print(f"[{row['checked_at']}] Status: {row['status']}")
    else:
        print("❌ NO RECENT HEARTBEATS FOUND.")

    # 2. Outreach check (last 24h)
    cutoff_outreach = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    touches = sb.table("outbound_touches").select("id", count="exact").gte("ts", cutoff_outreach).execute()
    
    print("\n--- OUTREACH (Last 24h) ---")
    print(f"Total Touches: {touches.count}")

    # 3. Campaign Mode
    state = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
    mode = state.data[0]['status'] if state.data else 'unknown'
    print(f"\nCampaign Mode: {mode}")

    # 4. Recent Vapi Debug Logs
    vapi = sb.table("vapi_debug_logs").select("event_type", "normalized_phone", "lookup_result", "call_mode").order("id", desc=True).limit(5).execute()
    print("\n--- VAPI DEBUG LOGS (Recent) ---")
    if vapi.data:
        for row in vapi.data:
            print(f"Event: {row['event_type']} | Phone: {row['normalized_phone']} | Result: {row['lookup_result']} | Mode: {row['call_mode']}")
    else:
        print("No recent Vapi debug logs found.")

if __name__ == "__main__":
    verify_system_metrics()
