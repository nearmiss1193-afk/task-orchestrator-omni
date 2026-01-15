import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
client = create_client(url, key)

try:
    res = client.table('leads').select('*').limit(1).execute()
    if res.data:
        schema = {
            "columns": list(res.data[0].keys()),
            "sample_data": res.data[0]
        }
        with open('leads_schema_debug.json', 'w') as f:
            json.dump(schema, f, indent=2)
        print("Schema dumped to leads_schema_debug.json")
    else:
        print("No data found in leads table.")
except Exception as e:
    print(f"Error dumping schema: {e}")
