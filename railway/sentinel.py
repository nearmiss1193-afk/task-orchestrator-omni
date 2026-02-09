import os
import time
import requests
import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# CONFIGURATION
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
MODAL_HEALTH_URL = os.environ.get("MODAL_HEALTH_URL") or "https://nearmiss1193-afk--ghl-omni-automation-health-check.modal.run"

def log_pulse(status, details=None):
    """Update system_state with sentinel pulse for AI awareness."""
    try:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        pulse_data = {
            "status": status,
            "last_pulse": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "details": details or {}
        }
        # Upsert sentinel status into system_state
        sb.table("system_state").upsert({
            "key": "sentinel_pulse",
            "status": status,
            "meta": pulse_data
        }, on_conflict="key").execute()
        print(f"[SENTINEL] Pulse logged: {status}")
    except Exception as e:
        print(f"⚠️ [SENTINEL] Pulse log failed: {e}")

def check_modal():
    """Check if Modal endpoint is alive."""
    try:
        resp = requests.get(MODAL_HEALTH_URL, timeout=15)
        if resp.status_code == 200:
            return True, "Modal Healthy"
        return False, f"Modal Degraded: {resp.status_code}"
    except Exception as e:
        return False, f"Modal Error: {str(e)}"

def trigger_healing():
    """PLACEHOLDER: In a real production environment, this would call 'modal deploy deploy.py'."""
    # Since we are in a protected environment, we log the intent and update the status.
    # In full production, we would use a subprocess or a specialized Modal redeploy hook.
    print("[SENTINEL] CRITICAL FAILURE DETECTED. AUTO-HEALING TRIGGERED.")
    log_pulse("HEALING", {"action": "Redeploy triggered (simulated)", "ts": datetime.datetime.utcnow().isoformat()})

def main_loop():
    print("SOVEREIGN SENTINEL ONLINE (RAILWAY)")
    consecutive_failures = 0
    
    while True:
        try:
            is_healthy, msg = check_modal()
            if is_healthy:
                print(f"[SENTINEL] {msg}")
                log_pulse("HEALTHY", {"message": msg})
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                print(f"[SENTINEL] Failure {consecutive_failures}: {msg}")
                log_pulse("DEGRADED", {"message": msg, "strikes": consecutive_failures})
                
                # If dead for 3 consecutive checks (15 mins), trigger healing
                if consecutive_failures >= 3:
                    trigger_healing()
                    consecutive_failures = 0 # Reset after healing attempt
        
        except Exception as e:
            print(f"🔥 [SENTINEL] Loop Error: {e}")
            
        time.sleep(300) # 5-minute heartbeat

if __name__ == "__main__":
    main_loop()
