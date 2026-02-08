import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env')
load_dotenv('.secrets/secrets.env')

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print(f"URL: {url[:30]}..." if url else "URL: MISSING")
print(f"Key: {key[:20]}..." if key else "Key: MISSING")

s = create_client(url, key)
r = s.table('customer_memory').select('*').execute()
print(f"\n=== CUSTOMER_MEMORY RECORDS: {len(r.data)} ===")
for x in r.data:
    print(f"\nPhone: {x.get('phone_number')}")
    print(f"Last: {x.get('last_interaction')}")
    print(f"Context: {x.get('context_summary')}")
