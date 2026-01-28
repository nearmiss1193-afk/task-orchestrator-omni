import os
import sys
import datetime
from dotenv import load_dotenv

# Load env in case we can hit Supabase
load_dotenv()

LOG_FILE = "orchestrator_logs.txt"

def broadcast(message, level="INFO"):
    timestamp = datetime.datetime.now().isoformat()
    log_line = f"[{timestamp}] [{level}] {message}"
    
    # 1. Write to local log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
        
    print(f"📣 BROADCAST: {log_line}")

    # 2. Try Supabase (Best Effort)
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
        if url and key:
            sb = create_client(url, key)
            sb.table("brain_logs").insert({
                "message": message,
                "level": level,
                "timestamp": timestamp,
                "source": "ANTIGRAVITY_AGENT"
            }).execute()
            print("✅ Synced to Supabase")
    except Exception as e:
        print(f"⚠️ Supabase Sync Failed (Non-blocking): {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python broadcast_event.py 'Message' [LEVEL]")
        sys.exit(1)
        
    msg = sys.argv[1]
    lvl = sys.argv[2] if len(sys.argv) > 2 else "INFO"
    broadcast(msg, lvl)
