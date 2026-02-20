"""Debug system_state table — check schema and try different insert methods"""
import sys, os, requests, json
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# 1. Check what keys exist in system_state
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/system_state?select=*&limit=20",
    headers=headers
)
print("=== SYSTEM STATE ROWS ===")
with open("system_state_dump.txt", "w") as f:
    for row in resp.json():
        line = f"  key={row.get('key')} | status={row.get('status','')[:50]} | last_error={str(row.get('last_error',''))[:30]}"
        print(line)
        f.write(json.dumps(row) + "\n")

# 2. Try inserting prospector_last_run using REST API directly
from datetime import datetime, timezone, timedelta
old_ts = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()

# Try upsert with Prefer: resolution=merge-duplicates
headers2 = dict(headers)
headers2["Prefer"] = "resolution=merge-duplicates,return=representation"

resp2 = requests.post(
    f"{SUPABASE_URL}/rest/v1/system_state",
    headers=headers2,
    json={"key": "prospector_last_run", "status": old_ts}
)
print(f"\nUpsert result: {resp2.status_code}")
print(f"  Body: {resp2.text[:200]}")
