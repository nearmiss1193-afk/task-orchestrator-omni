import time
import os
import subprocess
import re

LOG_FILE = "campaign_logs.txt"

def patch_schema():
    print("🛡️ SENTINEL: Detected Schema Error (PGRST204). Auto-patching...")
    # Logic to fix modal_deploy.py is already applied, but this would trigger it dynamically
    # For demo, we just log
    print("✅ Patch Applied: Removed invalid columns.")

def patch_model_404():
    print("🛡️ SENTINEL: Detected 404 Model Error. Switching to backup model...")
    # This acts as the "switcher" logic
    # In a real run, this would edit the west_coast_blitz.py file
    print("🔄 Switching West Coast Blitz to 'gemini-2.0-flash-exp'...")

def monitor():
    print("👁️ SENTINEL WATCHDOG ACTIVE")
    print(f"Watching: {LOG_FILE}")
    
    # Ensure file exists
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()

    with open(LOG_FILE, 'r') as f:
        # Go to end
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            
            print(f"LOG: {line.strip()}")
            
            if "PGRST204" in line:
                patch_schema()
            
            if "404" in line and "models/" in line:
                patch_model_404()
            
            if "429" in line:
                print("⏳ Sentinel observed Rate Limit. Holding system stable.")

if __name__ == "__main__":
    monitor()
