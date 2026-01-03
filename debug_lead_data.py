import os
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(url, key)

print(f"Connecting to {url}...")

res = supabase.table("contacts_master").select("*").order("created_at", desc=True).limit(5).execute()

print(f"Found {len(res.data)} records.")
for i, record in enumerate(res.data):
    print(f"Record {i}: Name='{record.get('full_name')}', Company='{record.get('company_name')}', URL='{record.get('website_url')}'")
    # print(json.dumps(record, indent=2))
