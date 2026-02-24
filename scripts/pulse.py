import os, sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
sys.path.insert(0, '.')
load_dotenv('.env')
load_dotenv('.env.local')
from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

cutoff_5m = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
cutoff_15m = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
cutoff_1h = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()

r5 = supabase.table("outbound_touches").select("id", count="exact").gte("ts", cutoff_5m).execute()
r15 = supabase.table("outbound_touches").select("id", count="exact").gte("ts", cutoff_15m).execute()
r1h = supabase.table("outbound_touches").select("id", count="exact").gte("ts", cutoff_1h).execute()

e_today = supabase.table("outbound_touches").select("id", count="exact").eq("channel","email").gte("ts", today_start).execute()
s_today = supabase.table("outbound_touches").select("id", count="exact").eq("channel","sms").gte("ts", today_start).execute()
c_today = supabase.table("outbound_touches").select("id", count="exact").eq("channel","call").gte("ts", today_start).execute()

fresh = supabase.table("contacts_master").select("id", count="exact").in_("status", ["new","research_done"]).execute()
hb = supabase.table("system_health_log").select("checked_at").order("checked_at", desc=True).limit(1).execute()

print(f"Last 5 min: {r5.count}")
print(f"Last 15 min: {r15.count}")
print(f"Last 1 hour: {r1h.count}")
print(f"Email today: {e_today.count}")
print(f"SMS today: {s_today.count}")
print(f"Calls today: {c_today.count}")
print(f"Fresh leads: {fresh.count}")
print(f"Heartbeat: {hb.data[0]['checked_at'] if hb.data else 'NONE'}")
