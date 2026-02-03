import os
from supabase import create_client, Client

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🕵️ Probing brain_logs...")
try:
    res = supabase.table("brain_logs").select("*").limit(1).execute()
    print("✅ brain_logs ALIVE")
except Exception as e:
    print(f"❌ brain_logs DEAD: {e}")
