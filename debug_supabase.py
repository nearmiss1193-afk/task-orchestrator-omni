import os
import requests
from dotenv import load_dotenv

load_dotenv()

# We'll use the Supabase REST API to check if the table exists
URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not URL or not KEY:
    print("❌ Supabase credentials missing.")
    exit(1)

# Try to select from the table via REST
test_url = f"{URL}/rest/v1/asset_inbox?select=count"
headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Range": "0-9"
}

try:
    res = requests.get(test_url, headers=headers)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        print("✅ table 'asset_inbox' exists.")
    else:
        print(f"❌ table 'asset_inbox' might be missing: {res.text}")
except Exception as e:
    print(f"❌ Connection error: {e}")
