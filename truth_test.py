
import os
import json
import requests
from datetime import datetime, timedelta

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def check_outreach():
    if not SUPABASE_KEY:
        print("❌ Missing SUPABASE_KEY")
        return

    # Check outreach in last 60 minutes
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. Check outbound_touches
    params = {
        "select": "id,ts",
        "ts": f"gt.{datetime.utcnow() - timedelta(minutes=60)}"
    }
    
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/outbound_touches", headers=headers, params=params)
        touches = res.json()
        print(f"✅ Recent Outreach Touches (60m): {len(touches)}")
        if touches:
            print(f"   Last touch at: {touches[0].get('ts')}")
    except Exception as e:
        print(f"❌ Error checking touches: {e}")

    # 2. Check system_health_log (Heartbeats)
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/system_health_log?select=checked_at&order=checked_at.desc&limit=1", headers=headers)
        hb = res.json()
        if hb:
            print(f"✅ Last Heartbeat: {hb[0].get('checked_at')}")
        else:
            print("❌ No heartbeats found")
    except Exception as e:
        print(f"❌ Error checking heartbeats: {e}")

if __name__ == "__main__":
    check_outreach()
