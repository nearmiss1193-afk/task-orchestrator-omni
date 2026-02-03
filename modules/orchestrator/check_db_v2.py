from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not url or not key:
    print("Error: Supabase URL or Key missing in .env.local")
    exit(1)

supabase = create_client(url, key)

try:
    # Try a simple select to see if table exists
    supabase.table('staged_replies').select('*').limit(1).execute()
    print("Table exists.")
except Exception as e:
    print(f"Table check failed: {e}")
