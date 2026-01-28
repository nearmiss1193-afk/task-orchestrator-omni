import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
sb = create_client(url, key)

print("--- RECENT BRAIN LOGS ---")
logs = sb.table("brain_logs").select("*").order("timestamp", desc=True).limit(20).execute()
for l in logs.data:
    print(f"[{l['timestamp']}] {l['message']}")

print("\n--- RECENT OUTREACH (TODAY) ---")
from datetime import datetime, timezone
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
touches = sb.table("outbound_touches").select("*").gte("ts", today).execute()
print(f"Found {len(touches.data)} touches for today.")
for t in touches.data:
    print(f"[{t['ts']}] {t['channel']} - {t['company']}")
