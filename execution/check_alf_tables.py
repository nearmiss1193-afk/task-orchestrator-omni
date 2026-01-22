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

print("Checking ALF tables...")
try:
    # Try selecting from alf_facilities
    res = supabase.table("alf_facilities").select("count", count="exact", head=True).execute()
    print(f"✅ Table 'alf_facilities' EXISTS. Count: {res.count}")
    
    # Try selecting from alf_referrals
    res2 = supabase.table("alf_referrals").select("count", count="exact", head=True).execute()
    print(f"✅ Table 'alf_referrals' EXISTS. Count: {res2.count}")
    
except Exception as e:
    print(f"❌ Table check failed: {e}")
    print("Likely need to run 'scripts/alf_referral_schema.sql'")
