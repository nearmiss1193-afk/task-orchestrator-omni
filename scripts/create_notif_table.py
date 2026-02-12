"""Create vapi_call_notifications table for dedup tracking"""
import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

from supabase import create_client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(url, key)

# Try to create via RPC or just test an insert+delete
# Supabase doesn't support DDL via the REST API, so let's just test if the table exists
try:
    r = sb.table('vapi_call_notifications').select('call_id').limit(1).execute()
    print(f"Table exists! Rows: {len(r.data)}")
except Exception as e:
    err_str = str(e)
    if '42P01' in err_str or 'does not exist' in err_str:
        print("Table does not exist. Creating via SQL...")
        # Use the SQL API
        import requests
        sql = """
        CREATE TABLE IF NOT EXISTS vapi_call_notifications (
            id BIGSERIAL PRIMARY KEY,
            call_id TEXT UNIQUE NOT NULL,
            customer_phone TEXT,
            notified_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        r = requests.post(f'{url}/rest/v1/rpc/exec_sql', 
                         headers=headers,
                         json={'sql': sql})
        if r.status_code in [200, 201]:
            print("Table created!")
        else:
            print(f"SQL RPC failed ({r.status_code}): {r.text[:200]}")
            print("\nManual SQL needed:")
            print(sql)
            print("\nThe monitor will still work - it just won't deduplicate.")
    else:
        print(f"Error: {e}")
