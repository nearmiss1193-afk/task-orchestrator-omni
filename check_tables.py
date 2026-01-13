"""Check what tables exist and their structure"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

sb = create_client(url, key)

# Try different table names that might exist
tables_to_check = ['leads', 'contacts_master', 'contacts', 'prospects', 'brain_logs']

for table in tables_to_check:
    try:
        result = sb.table(table).select('*').limit(1).execute()
        count = len(result.data) if result.data else 0
        print(f"✅ {table}: EXISTS ({count} sample rows)")
        if result.data:
            print(f"   Columns: {list(result.data[0].keys())}")
    except Exception as e:
        err = str(e)
        if 'does not exist' in err.lower() or '42P01' in err:
            print(f"❌ {table}: NOT FOUND")
        else:
            print(f"⚠️ {table}: ERROR - {err[:80]}")
