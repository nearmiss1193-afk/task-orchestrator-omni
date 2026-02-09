import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd())
from modules.database.supabase_client import get_supabase

# Load secrets
load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

def list_tables():
    sb = get_supabase()
    print("🔍 Listing Supabase Tables...")
    try:
        # Querying information_schema to see all table names
        res = sb.rpc("get_tables", {}).execute() # If RPC exists
    except:
        # Fallback to direct query if RPC doesn't exist (might need to check permissions)
        try:
            res = sb.table("contacts_master").select("*").limit(1).execute()
            print("✅ Successfully connected to contacts_master")
            # We already know contacts_master, customer_memory, conversation_logs, vapi_debug_logs exist.
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    list_tables()
