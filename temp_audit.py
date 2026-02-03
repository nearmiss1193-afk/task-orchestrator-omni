import os
from supabase import create_client
from datetime import datetime, timedelta

url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjE5MTc1MiwiZXhwIjoyMDUxNzY3NzUyfQ.GvYAnL381xdX8D6jHpTYokgtTZfv6sv0FCAmlfGhug81xdX"

s = create_client(url, key)
yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()

total = s.table("contacts_master").select("id", count="exact").execute().count
new_24h = s.table("contacts_master").select("id", count="exact").gt("created_at", yesterday).execute().count
touches_24h = s.table("outbound_touches").select("id", count="exact").gt("ts", yesterday).execute().count

print(f"TOTAL_LEADS: {total}")
print(f"NEW_24H: {new_24h}")
print(f"TOUCHES_24H: {touches_24h}")
