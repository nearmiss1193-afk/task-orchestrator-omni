import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load env
sys.path.append(os.getcwd())
load_dotenv('.env.local')

def debug_connection():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    print(f"URL: {url}")
    # Don't print full key
    print(f"Key Length: {len(key) if key else 0}")

    if not url or not key:
        print("❌ Error: Supabase credentials missing.")
        return

    try:
        supabase = create_client(url, key)
        # Try a very simple query
        print("Attempting to select count from contacts_master...")
        res = supabase.table("contacts_master").select("count", count="exact").limit(1).execute()
        print(f"✅ Success! Count: {res.count}")
        
        # Try the outreach query again but without neq null filter which might be tricky if column doesn't exist
        print("Checking column existence...")
        res = supabase.table("contacts_master").select("last_outreach_at").limit(1).execute()
        print("✅ Column 'last_outreach_at' exists.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_connection()
