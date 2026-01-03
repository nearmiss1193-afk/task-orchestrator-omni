
import os
from supabase import create_client
from dotenv import load_dotenv
import time

load_dotenv()

url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(url, key)

print("--- FETCHING LAST 10 LOGS ---")
res = supabase.table("brain_logs").select("*").order("timestamp", desc=True).limit(10).execute()

for log in res.data:
    print(f"[{log['timestamp']}] {log['message']}")
