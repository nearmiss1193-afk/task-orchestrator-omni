import os
from dotenv import load_dotenv
load_dotenv(".env")
from supabase import create_client
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
r = sb.table("system_health_log").select("*").eq("check_name","call_alert").order("checked_at",desc=True).limit(3).execute()
for row in r.data:
    ts = row.get("checked_at","")
    msg = row.get("message","")[:120]
    meta = row.get("metadata",{}) or {}
    name = meta.get("caller_name","")
    phone = meta.get("caller_phone","")
    print(f"TIME: {ts}")
    print(f"MSG: {msg}")
    print(f"CALLER: {name} | PHONE: {phone}")
    print("---")
if not r.data:
    print("NO call_alert rows found")
