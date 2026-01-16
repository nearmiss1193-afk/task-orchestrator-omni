import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

res = supabase.table('leads').select('*').limit(1).execute()
if res.data:
    print("Schema keys:", sorted(res.data[0].keys()))
else:
    print("No leads found to inspect schema.")
