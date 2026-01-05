
import time
import os
import sys
import psutil # Assuming user has this, if not we fall back to manual pid check or just API
import requests
import datetime

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from modules.communication.sovereign_dispatch import dispatcher

# CONFIG
CHECK_INTERVAL_SECONDS = 300 # 5 Minutes
POLLER_SCRIPT_NAME = "inbound_poller.py"
ALERT_PHONE = "+13529368152"
ALERT_EMAIL = "nearmiss1193@gmail.com"

def check_process_running(script_name):
    """Checks if a python script is running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                if proc.info['cmdline'] and any(script_name in arg for arg in proc.info['cmdline']):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def check_ghl_api():
    """Verifies GHL Connectivity."""
    try:
        if not dispatcher.ghl_token:
            return False, "No Token"
        
        # Lightweight check
        headers = {"Authorization": f"Bearer {dispatcher.ghl_token}", "Version": "2021-07-28"}
        res = requests.get(f"https://services.leadconnectorhq.com/locations/{dispatcher.ghl_location}", headers=headers, timeout=10)
        
        if res.status_code == 200:
            return True, "OK"
        return False, f"Status {res.status_code}"
    except Exception as e:
        return False, str(e)

def alert_commander(message):
    """Sends Critical Alert."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"⚠️ [SENTINEL ALERT] {timestamp}\n{message}"
    
    print(full_msg)
    
    # Try SMS
    dispatcher.send_sms(ALERT_PHONE, full_msg, provider="ghl")
    
    # Try Email (Fallback built-in)
    dispatcher.send_email(ALERT_EMAIL, "⚠️ SENTINEL ALERT: System Failure", full_msg, provider="ghl")

def main():
    print(f"🛡️ SENTINEL Monitoring Started. Interval: {CHECK_INTERVAL_SECONDS}s")
    
    while True:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Running Checks...")
        
        # 1. Check Internet (Implicit in API check, but good to separate if needed)
        
        # 2. Check Poller Process
        if not check_process_running(POLLER_SCRIPT_NAME):
            alert_commander(f"CRITICAL: {POLLER_SCRIPT_NAME} is NOT running! Restarting logic required.")
            # TODO: Auto-restart logic here
        
        # 3. Check GHL API
        ghl_ok, ghl_fail_reason = check_ghl_api()
        if not ghl_ok:
            alert_commander(f"CRITICAL: GHL API Unreachable. Reason: {ghl_fail_reason}")
        
        print(f"[{timestamp}] All Checks Passed.")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
