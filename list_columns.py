import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load env
sys.path.append(os.getcwd())
load_dotenv('.env.local')

def list_schema():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    
    supabase = create_client(url, key)
    
    try:
        # Try a different table that we know exists or list tables if possible
        # Or just try to select * limit 1 to see keys
        print("Selecting 1 row from contacts_master...")
        res = supabase.table("contacts_master").select("*").limit(1).execute()
        if res.data:
            print("Columns found:", res.data[0].keys())
        else:
            print("Table exists but is empty.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_schema()
