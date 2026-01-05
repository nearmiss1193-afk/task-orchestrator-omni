
import time
import requests
import json
import os
from datetime import datetime

# CONFIG
CORTEX_URL = "http://localhost:8000/execute"
# For PoC, we watch a local file. In production, this polls Supabase.
CLOUD_QUEUE_FILE = "cloud_commands.json" 

def check_cloud_queue():
    """
    Simulates polling a cloud database (Supabase) by reading a local JSON file.
    """
    if not os.path.exists(CLOUD_QUEUE_FILE):
        return None
    
    try:
        with open(CLOUD_QUEUE_FILE, "r") as f:
            commands = json.load(f)
            
        if not commands:
            return None
            
        # Get next command
        cmd = commands.pop(0)
        
        # Save back empty/reduced list
        with open(CLOUD_QUEUE_FILE, "w") as f:
            json.dump(commands, f)
            
        return cmd
    except Exception as e:
        print(f"⚠️ Uplink Error: {e}")
        return None

def main():
    print("📡 Sovereign Uplink Bridge Active...")
    print("   Connecting [Cloud Queue] -> [Local Cortex]")
    
    while True:
        command = check_cloud_queue()
        
        if command:
            print(f"⚡ INCOMING COMMAND: {command}")
            try:
                res = requests.post(CORTEX_URL, json=command)
                print(f"   ✅ Execution Status: {res.status_code} - {res.json()}")
            except Exception as e:
                print(f"   ❌ Execution Failed: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
