import sys
import os
import requests
import datetime
from dotenv import load_dotenv

# Add root to sys.path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

try:
    from modules.database.supabase_client import get_supabase
except ImportError:
    print(f"DEBUG: Current sys.path: {sys.path}")
    raise

load_dotenv()

def get_doctor_report():
    print("\n[DOCTOR] SYSTEM DIAGNOSIS")
    print("=" * 40)
    
    sentinel_status = "UNKNOWN"
    last_pulse = "NEVER"
    
    try:
        sb = get_supabase()
        if not sb:
            print("ERROR: Supabase Client Initialization Failed")
            return
            
        res = sb.table("system_state").select("*").eq("key", "sentinel_pulse").execute()
        if res.data and len(res.data) > 0:
            data = res.data[0]
            sentinel_status = data.get("status", "UNKNOWN")
            last_pulse = data.get("meta", {}).get("last_pulse", "UNKNOWN")
    except Exception as e:
        print(f"ERROR reading Sentinel pulse: {e}")

    print(f"[SENTINEL] status: {sentinel_status}")
    print(f"[PULSE]    last:   {last_pulse}")

    # 2. Check Modal Brain
    modal_url = "https://nearmiss1193-afk--ghl-omni-automation-health-check.modal.run"
    try:
        resp = requests.get(modal_url, timeout=10)
        brain_status = "HEALTHY" if resp.status_code == 200 else f"DEGRADED ({resp.status_code})"
    except:
        brain_status = "OFFLINE"
    
    print(f"[BRAIN]    Modal:  {brain_status}")

    # 3. Check Outreach State
    try:
        touch = sb.table("outbound_touches").select("ts").order("ts", desc=True).limit(1).execute()
        last_outreach = touch.data[0].get("ts") if touch.data else "None"
        print(f"[OUTREACH] Last:   {last_outreach}")
    except:
        print("[OUTREACH] Last:   Unknown")

    print("=" * 40)
    
    if sentinel_status == "HEALTHY" and brain_status == "HEALTHY":
        print("SYSTEM READY - Proceed with confidence.")
    else:
        print("ATTENTION: System requires stabilization before scale.")

if __name__ == "__main__":
    get_doctor_report()
