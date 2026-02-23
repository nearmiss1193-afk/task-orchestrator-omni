import os
import time
from dotenv import load_dotenv
from supabase import create_client

# Load from the Next.js portal .env
load_dotenv('apps/portal/.env.local')

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Polling for 'body' column existence...")
while True:
    try:
        response = supabase.table("outbound_touches").select("body").limit(1).execute()
        print("\n✅ SUCCESS: The user has created the 'body' column!")
        break
    except Exception as e:
        if '42703' in str(e):
            print(".", end="", flush=True)
        else:
            print(f"Unknown error: {e}")
            break
    time.sleep(5)
