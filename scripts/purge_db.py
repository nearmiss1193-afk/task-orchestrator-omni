import os
import asyncio
from supabase import create_client, Client

# --- CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Missing Supabase Credentials")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def purge_all_data():
    print("⚠️  WARNING: INITIATING REALITY PROTOCOL (DATA PURGE) ⚠️")
    print("This will DELETE ALL records from 'contacts_master'.")
    print("Waiting 5 seconds... (Ctrl+C to Cancel)")
    await asyncio.sleep(5)
    
    try:
        # 1. Count current records
        count_res = supabase.table("contacts_master").select("*", count="exact").execute()
        total = count_res.count
        print(f"📉 Current Target Count: {total}")
        
        if total == 0:
            print("✅ Database is already empty.")
            return

        # 2. Delete All (using neq 0 as valid filter to catch all IDs)
        # Supabase requires a WHERE clause for delete usually. 
        # We will delete where id is not 0 (assuming IDs are present)
        # Or better, logic to delete in batches if massive, but for 1500 it's fine.
        
        print("🔥 PURGING DATA...")
        # Since 'id' is distinct, we can use a wide filter
        res = supabase.table("contacts_master").delete().neq("ghl_contact_id", "0").execute()
        
        # 3. Verify
        verify_res = supabase.table("contacts_master").select("*", count="exact").execute()
        print(f"✅ PURGE COMPLETE. Remaining Records: {verify_res.count}")
        
    except Exception as e:
        print(f"❌ PURGE FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(purge_all_data())
