
import requests
import json
import time

# Service Role Key
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

data = {
    "call_id": f"test-direct-{int(time.time())}",
    "assistant_id": "test-assistant",
    "sentiment": "positive",
    "metadata": {"summary": "Direct insert test."}
}

print(f"Inserting into {SUPABASE_URL}/rest/v1/call_transcripts...")
r = requests.post(f"{SUPABASE_URL}/rest/v1/call_transcripts", headers=headers, json=data)

print(f"Status: {r.status_code}")
print(r.text)
