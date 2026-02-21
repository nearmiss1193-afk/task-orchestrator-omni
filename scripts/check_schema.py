import os
import requests
import json
from dotenv import load_dotenv

# Load local .env
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_KEY:
    print("❌ Error: Missing Supabase Key")
    exit(1)

# Using SQL API to add column if not exists
sql = "ALTER TABLE contacts_master ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0;"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

try:
    # Modal environments usually have a direct SQL endpoint or we use the REST API to execute if enabled
    # Since we don't have a direct SQL client, we'll try to use the REST API to check if column exists first
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/contacts_master?limit=1", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        if data and "score" in data[0]:
            print("✅ 'score' column already exists.")
        else:
            print("🕒 'score' column missing. Attempting to add via RPC if available, or just letting prospector handle it (it uses upsert).")
            # If we can't run SQL, we'll rely on the user running the SQL in the Supabase Dashboard
            print("⚠️ ACTION REQUIRED: Run this SQL in your Supabase SQL Editor:")
            print("ALTER TABLE contacts_master ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0;")
except Exception as e:
    print(f"❌ Error checking schema: {e}")
