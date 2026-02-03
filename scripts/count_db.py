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

async def count_data():
    try:
        # 1. Count current records
        count_res = supabase.table("contacts_master").select("*", count="exact", head=True).execute()
        total = count_res.count
        print(f"📊 LIVE TARGET COUNT: {total}")
        
        if total > 0:
            print("✅ REALITY VERIFIED. Data is present.")
        else:
            print("⚠️ ZERO RECORDS FOUND. Sync Failed or GHL is Empty.")
            
    except Exception as e:
        print(f"❌ COUNT FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(count_data())
