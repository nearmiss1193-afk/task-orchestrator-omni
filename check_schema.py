
import os
import requests
import json



# Key from temp_env.txt (Confirmed Service Role via decoding)
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"



if not SUPABASE_KEY:
    print("No Supabase Key Found")
    exit()

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print(f"Checking {SUPABASE_URL}...")

# Check call_transcripts
r = requests.get(f"{SUPABASE_URL}/rest/v1/call_transcripts?select=*&limit=1", headers=headers)
if r.ok:
    data = r.json()
    if data:
        print("Columns:", list(data[0].keys()))
    else:
        print("Table exists but empty")
else:
    print(f"Error: {r.status_code} {r.text}")
