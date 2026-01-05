
import time
import requests
import json
import os
from datetime import datetime

# CONFIG
CORTEX_URL = "http://localhost:8000/execute"
# For PoC, we watch a local file. In production, this polls Supabase.
CLOUD_QUEUE_FILE = "cloud_commands.json" 


# DB Config
import pg8000.native
import ssl
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url: return None
    try:
        result = urlparse(db_url)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        return pg8000.native.Connection(
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432,
            database=result.path[1:],
            ssl_context=ssl_context
        )
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def check_cloud_queue():
    """Polls Supabase for pending commands."""
    con = get_db_connection()
    if not con: return None
    
    try:
        # Fetch oldest pending command
        rows = con.run("SELECT id, command FROM commands WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1")
        
        if not rows:
            con.close()
            return None
            
        cmd_id, cmd_text = rows[0]
        
        # Mark as processing
        con.run("UPDATE commands SET status = 'processing' WHERE id = :id", id=cmd_id)
        con.close()
        
        return {"id": cmd_id, "command": cmd_text}
        
    except Exception as e:
        print(f"⚠️ Uplink Error: {e}")
        if con: con.close()
        return None

def complete_command(cmd_id, result):
    con = get_db_connection()
    if con:
        try:
            con.run("UPDATE commands SET status = 'completed' WHERE id = :id", id=cmd_id)
            con.close()
        except: pass

def main():
    print("📡 Sovereign Uplink Bridge V2.0 (DB Enabled)...")
    print("   Connecting [Supabase] -> [Local Cortex]")
    
    while True:
        cmd_obj = check_cloud_queue()
        
        if cmd_obj:
            command = cmd_obj['command']
            print(f"⚡ INCOMING COMMAND: {command}")
            try:
                # Execute via Cortex
                res = requests.post(CORTEX_URL, json={"command": command})
                print(f"   ✅ Execution Status: {res.status_code}")
                # Mark Complete
                complete_command(cmd_obj['id'], "success")
            except Exception as e:
                print(f"   ❌ Execution Failed: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
