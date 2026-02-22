import os
if not os.environ.get("SUPABASE_URL"):
    from dotenv import load_dotenv
    load_dotenv()
from modules.database.supabase_client import get_supabase

def run_checks():
    sb = get_supabase()
    
    print("=== 6-POINT VERIFICATION CHECKS ===")
    
    # Check 1: Campaign mode
    try:
        res = sb.table("system_state").select("*").eq("key", "campaign_mode").execute()
        mode = res.data[0]["status"] if res.data else "UNKNOWN"
        print(f"Campaign Mode: {mode}")
    except Exception as e:
        print(f"Campaign Mode check failed: {e}")
    
    # Check 2: Outbound touches
    try:
        from datetime import datetime, timedelta, timezone
        twenty_four_hours_ago = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        res2 = sb.table("outbound_touches").select("id", count="exact").gt("ts", twenty_four_hours_ago).execute()
        count_24h = res2.count if res2.count else 0
        print(f"Sent 24h: {count_24h}")
    except Exception as e:
        print(f"Sent 24h check failed: {e}")

    # Check 3: Opens 7d
    try:
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        res3 = sb.table("outbound_touches").select("id", count="exact").eq("opened", True).gt("ts", seven_days_ago).execute()
        opens_7d = res3.count if res3.count else 0
        print(f"Opens 7d: {opens_7d}")
    except Exception as e:
        print(f"Opens 7d check failed: {e}")
    
    # Check 4: Replies 7d
    try:
        res4 = sb.table("outbound_touches").select("id", count="exact").eq("replied", True).gt("ts", seven_days_ago).execute()
        replies_7d = res4.count if res4.count else 0
        print(f"Replies 7d: {replies_7d}")
    except Exception as e:
        print(f"Replies 7d check failed: {e}")

    # Check 5: Pipeline remaining
    try:
        res5 = sb.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).execute()
        pipeline = res5.count if res5.count else 0
        print(f"Pipeline (new/research_done): {pipeline}")
    except Exception as e:
        print(f"Pipeline check failed: {e}")

    # Check 6: Heartbeat
    try:
        res6 = sb.table("system_health_log").select("*").order("checked_at", desc=True).limit(1).execute()
        if res6.data:
            last_heartbeat = res6.data[0]["checked_at"]
            print(f"Last Heartbeat: {last_heartbeat}")
        else:
            print("Last Heartbeat: NONE")
    except Exception as e:
        print(f"Heartbeat check failed: {e}")

if __name__ == "__main__":
    run_checks()
