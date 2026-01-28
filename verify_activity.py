from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
import json

def check_logs():
    sb = get_supabase()
    print("--- Brain Logs ---")
    try:
        logs = sb.table("brain_logs").select("*").order("timestamp", desc=True).limit(10).execute()
        for log in logs.data:
            print(f"[{log['timestamp']}] {log['level']}: {log['message']}")
    except Exception as e:
        print(f"Error fetching brain_logs: {e}")

    print("\n--- Outbound Touches ---")
    try:
        touches = sb.table("outbound_touches").select("*").order("ts", desc=True).limit(5).execute()
        for touch in touches.data:
            print(f"[{touch['ts']}] {touch['channel']} to {touch['company']} (Status: {touch['status']})")
    except Exception as e:
        print(f"Error fetching touches: {e}")

if __name__ == "__main__":
    check_logs()
