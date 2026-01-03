import os
from supabase import create_client, Client

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🧪 Testing write to hiring_pipeline...")
try:
    payload = {"ghl_contact_id": "test_write_1", "status": "alive"}
    res = supabase.table("hiring_pipeline").upsert(payload, on_conflict="ghl_contact_id").execute()
    print("✅ WRITE SUCCESS.")
except Exception as e:
    print(f"❌ WRITE FAILED: {e}")
