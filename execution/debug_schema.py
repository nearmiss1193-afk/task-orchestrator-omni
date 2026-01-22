from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(url, key)

print("Checking contacts_master table...")
try:
    # Try to insert a minimal record
    test_record = {
        "company_name": "DEBUG_TEST_BIZ_" + os.urandom(4).hex(),
        "niche": "debug",
        "city": "debug_city"
    }
    print(f"Attempting insert: {test_record}")
    
    res = supabase.table("contacts_master").insert(test_record).execute()
    print("Insert success:", res.data)
    
except Exception as e:
    print(f"Insert failed: {e}")
    # Try fetching one row to see structure if possible (Python client doesn't give schema directly easily)
    try:
        res = supabase.table("contacts_master").select("*").limit(1).execute()
        if res.data:
            print("Existing row keys:", res.data[0].keys())
        else:
            print("Table empty, cannot infer keys.")
    except Exception as e2:
        print(f"Select failed: {e2}")
