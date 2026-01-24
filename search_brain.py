
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env.local')

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

print("🧠 SEARCHING BRAIN LOGS...")
try:
    # ILIKE query for sk_live
    res = supabase.table("brain_logs").select("*").ilike("message", "%sk_live%").limit(5).execute()
    if res.data:
        print("✅ Found potential keys in logs:")
        for log in res.data:
            print(f"[{log['timestamp']}] {log['message']}")
    else:
        print("❌ No 'sk_live' found in logs.")

    # Try searching for "gave all keys" or user input style logs if any
    res2 = supabase.table("brain_logs").select("*").ilike("message", "%stripe%").limit(10).order("timestamp", desc=True).execute()
    for log in res2.data:
        print(f"[{log['timestamp']}] {log['message']}")

except Exception as e:
    print(f"Error: {e}")
