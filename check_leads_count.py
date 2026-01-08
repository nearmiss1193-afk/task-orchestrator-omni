
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_leads():
    try:
        res = supabase.table('leads').select('*', count='exact').execute()
        print(f"Total Leads: {res.count}")
        if res.data:
            print(f"Sample Status: {res.data[0].get('status')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_leads()
