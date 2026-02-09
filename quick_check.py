"""Quick database check"""
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timezone, timedelta

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key: {key[:20]}..." if key else "Key: MISSING")

try:
    sb = create_client(url, key)
    
    # Check 1: Can we see contacts?
    contacts = sb.table("contacts_master").select("id", count="exact").limit(1).execute()
    print(f"\n✅ Contacts visible: {contacts.count}")
    
    # Check 2: Recent outreach?
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    outreach = sb.table("outbound_touches").select("*", count="exact").gte("ts", cutoff).execute()
    print(f"✅ Outreach (30 min): {outreach.count}")
    
    # Check 3: Campaign mode?
    mode = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
    if mode.data:
        print(f"✅ Campaign mode: {mode.data[0]['status']}")
    
    # Check 4: Heartbeat?
    heartbeat = sb.table("system_health_log").select("checked_at").order("checked_at", desc=True).limit(1).execute()
    if heartbeat.data:
        print(f"✅ Last heartbeat: {heartbeat.data[0]['checked_at']}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
