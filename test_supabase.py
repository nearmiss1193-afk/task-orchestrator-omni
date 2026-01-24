from supabase import create_client
import os

url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

print(f"Testing connection to {url}")
try:
    # Try positional
    print("Attempt 1: Positional args")
    cl = create_client(url, key)
    print("✅ Success 1")
except Exception as e:
    print(f"❌ Fail 1: {e}")

try:
    # Try keyword
    print("Attempt 2: Keyword args")
    cl = create_client(supabase_url=url, supabase_key=key)
    print("✅ Success 2")
except Exception as e:
    print(f"❌ Fail 2: {e}")

try:
    # Try Client direct
    from supabase import Client, ClientOptions
    print("Attempt 3: Client direct")
    cl = Client(supabase_url=url, supabase_key=key)
    print("✅ Success 3")
except Exception as e:
    print(f"❌ Fail 3: {e}")
