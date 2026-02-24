import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import Counter
from dotenv import load_dotenv
from modules.database.supabase_client import get_supabase

def check_status():
    load_dotenv()
    supabase = get_supabase()
    
    # Check contacts_master statuses
    print("--- contacts_master STATUS COUNTS ---")
    res = supabase.table("contacts_master").select("status").execute()
    counts = Counter([r.get("status") for r in res.data])
    for k, v in counts.items():
        print(f"{k}: {v}")
        
    print("\n--- veo_status COUNTS ---")
    res_veo = supabase.table("contacts_master").select("veo_status").execute()
    veo_counts = Counter([r.get("veo_status") for r in res_veo.data])
    for k, v in veo_counts.items():
        print(f"{k}: {v}")
        
    print("\n--- outbound_touches LAST 1 HOUR ---")
    try:
        from datetime import datetime, timedelta, timezone
        one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        touches = supabase.table("outbound_touches").select("*").gte("ts", one_hour_ago).execute()
        print(f"Touches in last 1 hour: {len(touches.data)}")
    except Exception as e:
        print(e)
        
    print("\n--- MODAL LOGS CHECK ---")
    import subprocess
    try:
        logs = subprocess.check_output(["python", "-m", "modal", "app", "logs", "ghl-omni-automation"], stderr=subprocess.STDOUT, encoding='utf-8')
        lines = logs.split("\n")
        print("\n".join(lines[-30:])) # print last 30 lines
    except Exception as e:
        print(f"Could not fetch Modal logs: {e}")

if __name__ == "__main__":
    check_status()
