
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
ALERT_PHONE = "+13529368152"
ALERT_EMAIL = "nearmiss1193@gmail.com"

# Services to Monitor (Name, Path)
MONITORED_SERVICES = [
    {
        "name": "inbound_poller.py",
        "path": "modules/communication/inbound_poller.py",
        "title": "Sarah Leed (Brain)"
    },
    {
        "name": "intake_server.py",
        "path": "modules/sourcing/intake_server.py",
        "title": "The Hunter (Intake)"
    },
    {
        "name": "uplink_bridge.py",
        "path": "Sovereign_Agent/uplink_bridge.py",
        "title": "Sovereign Bridge (Uplink)"
    }
]

def manage_process(service):
    """Ensures exactly ONE instance of the service is running."""
    script_name = service["name"]
    script_path = service["path"]
    
    procs = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'python' in proc.info['name'].lower():
                if any(script_name in arg for arg in cmdline):
                    procs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if len(procs) > 1:
        print(f"[SENTINEL] ⚠️  Conflict: {len(procs)} instances of {script_name}. Resolving...")
        # Sort by creation time (newest first)
        procs.sort(key=lambda p: p.create_time(), reverse=True)
        
        # Kill duplicates (all but first)
        for p in procs[1:]:
            try:
                print(f"   -> Killing {script_name} PID {p.pid}")
                p.kill()
            except:
                pass
        return True # Action taken
        
    elif len(procs) == 0:
        print(f"[SENTINEL] ❌ {service['title']} DOWN. Restarting...")
        alert_commander(f"Restoring Service: {service['title']}")
        try:
            # Use Start-Process for clean detachment
            cmd = ["powershell", "Start-Process", "python", "-ArgumentList", f'"{script_path}"', "-WindowStyle", "Minimized"]
            subprocess.run(cmd)
            return True
        except Exception as e:
            print(f"   [ERR] Restart Failed: {e}")
            return False
            
    return False # Healthy

def check_ghl_api():
    """Verifies GHL Connectivity."""
    try:
        if not dispatcher.ghl_token:
            return False, "No Token"
        
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
    # Try SMS/Email via Dispatch
    try:
        dispatcher.send_sms(ALERT_PHONE, full_msg, provider="ghl")
        dispatcher.send_email(ALERT_EMAIL, "⚠️ SENTINEL ALERT", full_msg, provider="ghl")
    except:
        pass

def main():
    print(f"🛡️ SENTINEL V2.0 Active. Monitoring {len(MONITORED_SERVICES)} Services.")
    
    while True:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Scanning Fleet...")
        
        # 1. Check all Services
        for service in MONITORED_SERVICES:
            manage_process(service)
        
        # 2. Check GHL API
        ghl_ok, ghl_fail_reason = check_ghl_api()
        if not ghl_ok:
            alert_commander(f"CRITICAL: GHL API Unreachable. Reason: {ghl_fail_reason}")
        
        print(f"[{timestamp}] Fleet Status: GREEN.")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
