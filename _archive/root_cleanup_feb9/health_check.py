import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timedelta

def run_health_check():
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    
    # Try to load from .env directly if load_dotenv() fails to populate os.environ
    if not url or not key:
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    parts = line.strip().split("=", 1)
                    if len(parts) != 2: continue
                    k, v = parts
                    val = v.strip('"').strip("'")
                    if k in ["NEXT_PUBLIC_SUPABASE_URL", "SUPABASE_URL"]: url = val
                    if k in ["SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_KEY"]: key = val
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return

    supabase = create_client(url, key)
    
    print("\n--- Health Check Results ---")
    
    # 1. Outreach Happening?
    try:
        res = supabase.table("outbound_touches").select("ts").gt("ts", (datetime.now() - timedelta(minutes=30)).isoformat()).execute()
        print(f"Outreach last 30m: {len(res.data)}")
        if res.data:
            print(f"Last sent: {max([r['ts'] for r in res.data])}")
    except Exception as e:
        print(f"Outreach Check Error: {e}")

    # 2. Heartbeat Working?
    try:
        res = supabase.table("system_health_log").select("checked_at, status").gt("checked_at", (datetime.now() - timedelta(minutes=15)).isoformat()).order("checked_at", desc=True).limit(5).execute()
        print(f"Heartbeats last 15m: {len(res.data)}")
        for r in res.data:
            print(f" - {r['checked_at']}: {r['status']}")
    except Exception as e:
        # Table might not exist yet if it's a new system
        print(f"Heartbeat Check Error: {e}")

    # 3. Campaign Mode Active?
    try:
        res = supabase.table("system_state").select("*").eq("key", "campaign_mode").execute()
        if res.data:
            print(f"Campaign Mode: {res.data[0]['status']}")
        else:
            print("Campaign Mode: Row missing")
    except Exception as e:
        print(f"Campaign Mode Check Error: {e}")

    # 4. Leads Available?
    try:
        res = supabase.table("contacts_master").select("status").execute()
        counts = {}
        for r in res.data:
            s = r['status']
            counts[s] = counts.get(s, 0) + 1
        print(f"Leads by status: {counts}")
    except Exception as e:
        print(f"Leads Check Error: {e}")

if __name__ == "__main__":
    run_health_check()
