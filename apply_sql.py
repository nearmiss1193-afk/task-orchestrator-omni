import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Missing Supabase credentials in .env")
    exit(1)

supabase = create_client(url, key)

sql = """
ALTER TABLE public.contacts_master ADD COLUMN IF NOT EXISTS website_url text;
NOTIFY pgrst, 'reload schema';
"""

try:
    # Try user-defined RPC 'exec_sql' with 'query' param
    print("Attempting to execute SQL via RPC 'exec_sql' (param: query)...")
    response = supabase.rpc("exec_sql", {"query": sql}).execute()
    print("Success:", response)
except Exception as e:
    print(f"FAILED: {e}")
