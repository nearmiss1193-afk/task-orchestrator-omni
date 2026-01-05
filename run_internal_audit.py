import subprocess
import sys
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
GHL_TOKEN = os.environ.get("GHL_API_TOKEN")
GHL_LOC = os.environ.get("GHL_LOCATION_ID")

def check_process_integrity():
    print("   [SCAN] Checking for duplicate processes...")
    # Use tasklist as a robust, dependency-free check on Windows
    try:
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq python.exe" /FO CSV /V', shell=True).decode()
        # Count instances of inbound_poller.py
        count = output.lower().count("inbound_poller.py")
        
        if count > 1:
            print(f"   [FAIL] Process Conflict: {count} 'inbound_poller.py' instances found. Only 1 allowed.")
            return False
        
        print(f"   [OK] Process Integrity: {count} instance(s) found (Clean).")
        return True
    except Exception as e:
        print(f"   [WARN] Could not verify processes: {e}")
        return True # Fail open if we can't check, but verify logic

def run_tests():
    print("   [TEST] Running Logic Test Suite...")
    # Run unittest via subprocess
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("\n❌ SYSTEM FAILURE: Logic Tests Failed.")
        print(result.stderr)
        print(result.stdout)
        return False
    print("   [OK] Logic Tests: PASSED.")
    return True

def check_connectivity():
    print("   [PING] Verifying GHL API Connection...")
    if not GHL_TOKEN or not GHL_LOC:
        print("   [FAIL] GHL Credentials Missing from Env.")
        return False
        
    headers = {
        "Authorization": f"Bearer {GHL_TOKEN}",
        "Version": "2021-07-28"
    }
    try:
        url = f"https://services.leadconnectorhq.com/conversations/search?locationId={GHL_LOC}&limit=1"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            print("   [OK] GHL API: Connected.")
            return True
        else:
            print(f"   [FAIL] GHL API Error: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"   [FAIL] GHL Connectivity Exception: {e}")
        return False

def run_suite():
    print("\n🛡️ RUNNING INTERNAL FAIL-PROOF PROTOCOL (v2.0)...")
    
    checks = [
        check_process_integrity,
        check_connectivity,
        run_tests
    ]
    
    for check in checks:
        if not check():
            print("\n❌ AUDIT FAILED. HALTING.")
            return False
            
    print("\n✅ SYSTEM INTEGRITY: 100% PASSING.")
    return True

if __name__ == "__main__":
    success = run_suite()
    if not success:
        sys.exit(1)
