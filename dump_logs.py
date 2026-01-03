
import os
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Missing Supabase credentials")
    exit(1)

supabase = create_client(url, key)

response = supabase.table("brain_logs").select("*").order("timestamp", desc=True).limit(50).execute()
data = response.data

with open("logs_dump.txt", "w", encoding="utf-8") as f:
    for log in data:
        f.write(f"[{log['timestamp']}] {log['message']}\n")

print("Logs written to logs_dump.txt")
