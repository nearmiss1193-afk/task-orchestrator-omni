from dotenv import load_dotenv
load_dotenv()

def check_readiness():
    from modules.database.supabase_client import get_supabase
    sb = get_supabase()
    
    # 1. Check Campaign Mode
    state = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
    mode = state.data[0]['status'] if state.data else "NOT FOUND"
    print(f"📡 Campaign Mode: {mode}")
    
    # 2. Check Lead Queue
    research_ready = sb.table("contacts_master").select("id", count="exact").eq("status", "new").execute()
    outreach_ready = sb.table("contacts_master").select("id", count="exact").eq("status", "research_done").execute()
    
    print(f"📊 Queue Stats:")
    print(f"   - Needs Research: {research_ready.count}")
    print(f"   - Ready for Outreach: {outreach_ready.count}")
    
    # 3. Last Heartbeat
    hb = sb.table("system_health_log").select("checked_at").order("checked_at", desc=True).limit(1).execute()
    last_hb = hb.data[0]['checked_at'] if hb.data else "NEVER"
    print(f"💓 Last Heartbeat: {last_hb}")

if __name__ == "__main__":
    check_readiness()
