import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

load_dotenv(".env")

from modules.database.supabase_client import get_supabase

def test_local_sync():
    print("🔍 LOCAL SYNC TEST")
    print(f"URL: {os.environ.get('NEXT_PUBLIC_SUPABASE_URL')}")
    
    sb = get_supabase()
    if not sb:
        print("❌ FAILED TO INIT SUPABASE")
        return

    try:
        res = sb.table("contacts_master").select("id", "full_name").limit(1).execute()
        print(f"✅ SUCCESS: Found {len(res.data)} leads.")
        if res.data:
            print(f" - Sample: {res.data[0]}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_local_sync()
