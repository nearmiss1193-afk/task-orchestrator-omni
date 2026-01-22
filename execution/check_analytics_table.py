from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not url or not key:
    print("Missing Supabase credentials")
    exit(1)

supabase = create_client(url, key)

print("Checking Analytics tables...")
try:
    # Try selecting from visitor_logs
    res = supabase.table("visitor_logs").select("count", count="exact", head=True).execute()
    print(f"✅ Table 'visitor_logs' EXISTS. Count: {res.count}")
    
except Exception as e:
    print(f"❌ Table check failed: {e}")
