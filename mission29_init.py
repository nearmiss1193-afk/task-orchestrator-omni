
import os
import datetime
import json
from supabase import create_client
from modules.governor.guardian_v2 import GuardianV2

# Config
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def init_mission_29():
    print(f"🏛️ Mission 29: Governor V2 Initialization at {datetime.datetime.now()}")
    
    supabase = None
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Supabase Connected")
        except Exception as e:
            print(f"⚠️ Supabase Init Failed: {e}")
    else:
        print("⚠️ Supabase Credentials missing. Running in SAFE MODE (Simulated).")

    # 1. Initialize Guardian V2
    guardian = GuardianV2(supabase)
    
    # 2. Run Diagnostic Protocol
    print("\nrunning execute_sovereign_protocol()...")
    report = guardian.execute_sovereign_protocol()
    print(json.dumps(report, indent=2))
    
    # 3. Test New Logic Specifically
    print("\nTesting Predictive Logic...")
    anomaly_report = guardian._predict_anomalies()
    print(f"Predictions: {anomaly_report}")
    
    print("\nTesting Resource Allocator...")
    resource_action = guardian._optimize_resources(report)
    print(f"Optimization: {resource_action}")

    # 4. Log Initialization Tag
    log_payload = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "level": "INFO",
        "component": "GovernorV2",
        "message": "Mission 29: Self-Healing Logic Active (Predictive + Resource)",
        "tag": "MISSION29_INIT"
    }
    
    if supabase:
        try:
            supabase.table("supervisor_logs").insert(log_payload).execute()
            print("\n✅ MISSION29_INIT Logged to DB.")
        except Exception as e:
             # Fallback
             print(f"\n⚠️ Database Log Failed: {e}")
             if "supervisor_logs" in str(e): # Table might be missing
                 supabase.table("brain_logs").insert({"message": str(log_payload), "level": "INFO", "timestamp": log_payload['timestamp']}).execute()
                 print("   -> Fallback to brain_logs successful.")
    else:
        print(f"\n[SIMULATION] DB Insert: {log_payload['tag']}")

if __name__ == "__main__":
    init_mission_29()
