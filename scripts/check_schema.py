import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd())
from modules.database.supabase_client import get_supabase

# Load secrets
load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

def check_schema():
    sb = get_supabase()
    print("🔍 Checking customer_memory schema...")
    res = sb.table("customer_memory").select("*").limit(1).execute()
    if res.data:
        print(f"📊 Columns: {list(res.data[0].keys())}")
        print(f"📊 Sample: {res.data[0]}")
    else:
        print("⚠️ No data in customer_memory")

if __name__ == "__main__":
    check_schema()
