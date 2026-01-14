
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: credentials missing")
    exit()

client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_status_counts():
    # Fetch all leads status
    res = client.table("leads").select("status").execute()
    data = res.data
    
    counts = {}
    for row in data:
        s = row.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
        
    print("--- Lead Status Counts ---")
    for k, v in counts.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    check_status_counts()
