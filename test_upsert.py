import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

try:
    res = supabase.table('leads').upsert({"company_name": "Test Lead", "status": "pending"}, on_conflict='company_name').execute()
    print("Success:", res)
except Exception as e:
    print("Full Error:", e)
