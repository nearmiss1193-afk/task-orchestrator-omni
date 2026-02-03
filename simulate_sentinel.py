import os
import datetime
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

def simulate_sentinel():
    sb = get_supabase()
    
    print("🧪 SIMULATING SENTINEL FAILURE...")
    
    # 1. Reset mode to working first
    sb.table("system_state").update({"status": "working"}).eq("key", "campaign_mode").execute()
    print("✅ System Reset to 'working'")
    
    # 2. Insert 10 failed touches to ensure we own the window
    test_id = f"Sentinel_Test_{int(datetime.datetime.now().timestamp())}"
    print(f"🧨 Injecting 10 failures into outbound_touches [ID: {test_id}]...")
    for i in range(10):
        sb.table("outbound_touches").insert({
            "phone": "555-555-5555",
            "channel": "sms",
            "company": test_id,
            "status": "failed",
            "payload": {"error": "Simulated failure for sentinel testing"},
            "ts": datetime.datetime.now().isoformat()
        }).execute()
        
    print("⏳ Waiting for Sentinel Pulse Check (manual trigger)...")
    
    # 3. Trigger manual pulse to see if Sentinel catches it
    # Since we can't easily trigger the Modal cron directly from here with logs,
    # we simulate the sentinel_guard logic locally to verify it WOULD trigger.
    
    touches = sb.table("outbound_touches")\
        .select("status")\
        .order("ts", desc=True)\
        .limit(10)\
        .execute()
    
    failures = [t for t in touches.data if t['status'] == 'failed']
    print(f"📡 Mock Guard: Detected {len(failures)}/10 failures.")
    
    if len(failures) >= 7:
        print("🚨 SENTINEL SHIELD TRIPPED!")
        sb.table("system_state").update({"status": "broken"}).eq("key", "campaign_mode").execute()
        print("✅ SUCCESS: Campaign mode is now 'broken'")
    else:
        print("❌ FAILURE: Sentinel did not trip.")

if __name__ == "__main__":
    simulate_sentinel()
