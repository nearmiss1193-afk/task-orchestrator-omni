"""
SELF-HEALING ORCHESTRATOR MONITOR
Monitors Modal health and auto-redeploys or falls back to local runner
"""
import requests
import time
import subprocess
from datetime import datetime

# Config
ORCHESTRATOR_URL = "https://nearmiss1193-afk--sovereign-orchestrator-health.modal.run"
RETRY_DELAY = 60  # seconds
MAX_RETRIES = 3
LOG_FILE = "monitor_log.txt"


def log(message: str):
    """Log with timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def check_orchestrator() -> bool:
    """Check if orchestrator is healthy"""
    try:
        r = requests.get(ORCHESTRATOR_URL, timeout=10)
        if r.status_code == 200:
            log("✅ Orchestrator healthy")
            return True
        else:
            log(f"⚠️ Orchestrator returned {r.status_code}")
            return False
    except Exception as e:
        log(f"❌ Orchestrator check failed: {e}")
        return False


def deploy_modal() -> bool:
    """Redeploy to Modal"""
    log("🔄 Attempting Modal redeploy...")
    try:
        result = subprocess.run(
            ["py", "-m", "modal", "deploy", "modal_orchestrator.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0 or "Created" in result.stdout:
            log("✅ Modal deploy successful")
            return True
        else:
            log(f"❌ Modal deploy failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        log(f"❌ Modal deploy error: {e}")
        return False


def start_local_runner() -> bool:
    """Start local fallback campaign runner"""
    log("🏠 Starting local fallback...")
    try:
        # Run multi-touch sequence in background
        subprocess.Popen(
            ["python", "multi_touch_sequence.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log("✅ Local runner started")
        return True
    except Exception as e:
        log(f"❌ Local runner failed: {e}")
        return False


def self_heal_orchestrator() -> bool:
    """Execute self-healing sequence"""
    log("🔧 SELF-HEAL TRIGGERED")
    
    # Step 1: Try redeploying to Modal
    for attempt in range(MAX_RETRIES):
        log(f"  Attempt {attempt + 1}/{MAX_RETRIES}")
        if deploy_modal():
            time.sleep(10)  # Wait for deployment
            if check_orchestrator():
                log("✅ Self-heal successful via Modal redeploy")
                return True
    
    # Step 2: Fall back to local runner
    log("⚠️ Modal redeploy failed, starting local fallback")
    return start_local_runner()


def monitor_loop():
    """Main monitoring loop"""
    log("=" * 50)
    log("ORCHESTRATOR MONITOR STARTED")
    log(f"Health URL: {ORCHESTRATOR_URL}")
    log(f"Check interval: {RETRY_DELAY}s")
    log("=" * 50)
    
    consecutive_failures = 0
    
    while True:
        ok = check_orchestrator()
        
        if ok:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            log(f"⚠️ Consecutive failures: {consecutive_failures}")
            
            if consecutive_failures >= 2:
                self_heal_orchestrator()
                consecutive_failures = 0
        
        time.sleep(RETRY_DELAY)


def check_once():
    """Single health check (for testing)"""
    log("Single health check...")
    ok = check_orchestrator()
    if not ok:
        log("Orchestrator DOWN")
        self_heal_orchestrator()
    return ok


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Single check mode
        check_once()
    else:
        # Continuous monitoring
        monitor_loop()
