
import os
import json
import time
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def debug_sync():
    # Test Data from JSON
    test_lead = {
        "name": "Michael Sanchez",
        "email": "michael@tampabayhvacexperts.com",
        "company": "Tampa Bay HVAC Experts",
        "city": "Tampa",
        "phone": "813-456-7890",
        "industry": "HVAC"
    }

    # Map to DB
    data = {
        "first_name": "Michael",
        "last_name": "Sanchez",
        "company_name": "Tampa Bay HVAC Experts",
        "email": "michael@tampabayhvacexperts.com",
        "phone": "813-456-7890",
        "city": "Tampa",
        "state": "FL",
        "industry": "HVAC",
        "source": "debug_sync",
        "status": "new",
        "created_at": time.strftime('%Y-%m-%d %H:%M:%S%z')
    }

    print("Attempting to insert test lead...")
    try:
        res = supabase.table('leads').insert(data).execute()
        print("✅ Success!")
        print(res.data)
    except Exception as e:
        with open("db_error.log", "w") as f:
            f.write(f"Error Type: {type(e)}\n")
            f.write(f"Error Args: {e.args}\n")
            f.write(f"Error Detail: {e}\n")
            if hasattr(e, 'code'): f.write(f"Error Code: {e.code}\n")
        print("❌ FAILED! See db_error.log")

if __name__ == "__main__":
    debug_sync()
