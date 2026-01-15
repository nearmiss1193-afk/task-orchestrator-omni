import os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
client = create_client(url, key)
try:
    res = client.table('leads').select('*').limit(1).execute()
    print(f"Data: {res.data[0]}")
except Exception as e:
    print(f"Error: {e}")
