"""Insert prospector_last_run — put timestamp in last_error field like cycle_index does"""
import os, requests
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=representation"
}

old_ts = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()

# First check what status values are allowed
check_resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/system_state?select=status&limit=5",
    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
)
print(f"Existing status values: {[r['status'] for r in check_resp.json()]}")

# Use 'working' as status (known valid) and store timestamp in last_error 
data = {
    "key": "prospector_last_run",
    "status": "working",
    "last_error": old_ts,
    "build_attempts": 0
}

resp = requests.post(
    f"{SUPABASE_URL}/rest/v1/system_state",
    headers=headers,
    json=data
)
print(f"Insert status: {resp.status_code}")
print(f"Response: {resp.text[:300]}")

if resp.status_code == 201:
    print(f"\n✅ prospector_last_run seeded! Timestamp: {old_ts}")
    print("Next heartbeat on Modal should trigger the prospector.")
else:
    print("\n❌ Still failing — may need to update deploy.py to handle this")
