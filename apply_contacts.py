import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

with open("create_contacts_master.sql", "r") as f:
    sql = f.read()

print("[Bridge] Applying Contacts Table...")
try:
    response = supabase.rpc("exec_sql", {"query": sql}).execute()
    print("✅ SUCCESS: Contacts Table Ready.")
except Exception as e:
    print(f"❌ BRIDGE FAILED: {e}")
