
import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def inspect():
    try:
        res = supabase.table('leads').select('*').limit(1).execute()
        if res.data:
            print("Existing Columns:")
            print(json.dumps(list(res.data[0].keys()), indent=2))
        else:
            print("No data to inspect columns from.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
