
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env.local')

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

print("🧠 SEARCHING BRAIN LOGS (BROAD)...")
try:
    # Broad search
    res = supabase.table("brain_logs").select("*").or_("message.ilike.%secret%,message.ilike.%key%,message.ilike.%sk_%,message.ilike.%pk_%").limit(20).order("timestamp", desc=True).execute()
    for log in res.data:
        print(f"[{log['timestamp']}] {log['message']}")

except Exception as e:
    print(f"Error: {e}")
