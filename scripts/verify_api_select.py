import os
from supabase import create_client, Client

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_selects():
    print("🕵️ Investigating contacts_master Selects...")
    
    # Test 1: Full Select
    try:
        print("1. Testing select('*')...")
        res = supabase.table("contacts_master").select("*").limit(1).execute()
        print("   ✅ Success")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test 2: Specific Columns
    try:
        print("2. Testing select('ghl_contact_id, status')...")
        res = supabase.table("contacts_master").select("ghl_contact_id, status").limit(1).execute()
        print("   ✅ Success")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        
    # Test 3: Count Only
    try:
        print("3. Testing count...")
        res = supabase.table("contacts_master").select("*", count="exact", head=True).execute()
        print(f"   ✅ Success: {res.count}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    test_selects()
