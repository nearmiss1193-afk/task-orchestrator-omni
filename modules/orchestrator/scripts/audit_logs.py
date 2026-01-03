import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env.local")

def get_supabase() -> Client:
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def log_audit():
    print("--- MISSION: LOG AUDIT ---")
    supabase = get_supabase()
    
    # Check for recent logs
    try:
        logs = supabase.table("brain_logs").select("*").order("timestamp", desc=True).limit(20).execute()
        if logs.data:
            for l in logs.data:
                print(f"[{l['timestamp']}] {l['message']}")
        else:
            print("No recent logs found.")
    except Exception as e:
        print(f"Error reading logs: {str(e)}")

if __name__ == "__main__":
    log_audit()
