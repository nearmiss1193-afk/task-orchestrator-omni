import requests
import json

URL = "https://rzcpfwkygdvoshtwxncs.supabase.co/rest/v1/"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json"
}

# We use RPC exec_sql which should exist if the user ran the migration
sql = """
SELECT column_name, is_nullable, data_type 
FROM information_schema.columns 
WHERE table_name = 'conversation_events' 
ORDER BY ordinal_position;
"""

try:
    r = requests.post(URL + "rpc/exec_sql", headers=HEADERS, json={"query": sql})
    if r.ok:
        print(json.dumps(r.json(), indent=2))
    else:
        print(f"Error: {r.status_code} {r.text}")
except Exception as e:
    print(f"Exception: {e}")
