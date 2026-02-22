import os
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

sb = get_supabase()

print("system_state:")
print(sb.table("system_state").select("*").limit(1).execute().data)

print("system_health_log:")
print(sb.table("system_health_log").select("*").limit(1).execute().data)
