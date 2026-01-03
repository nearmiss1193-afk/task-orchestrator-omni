
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
# Use Service Role Key to bypass RLS for this admin check
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

print(f"URL: {url}")
print(f"Key Length: {len(key) if key else 0}")

if not url or not key:
    print("Missing credentials!")
    exit(1)

supabase = create_client(url, key)

print("Checking 'brain_logs' table...")
try:
    # Attempt to select from the table
    res = supabase.table("brain_logs").select("*").limit(1).execute()
    print("Table exists!")
    print(res.data)
except Exception as e:
    print(f"Error accessing table: {e}")

print("\nAttempting Insert...")
try:
    res = supabase.table("brain_logs").insert({"message": "Sovereign Stack Admin Check"}).execute()
    print("Insert success!")
    print(res.data)
except Exception as e:
    print(f"Insert failed: {e}")
