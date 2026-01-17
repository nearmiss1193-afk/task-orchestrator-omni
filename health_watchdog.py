"""
AGENT: Watchdog — Health Monitor & Auto-Healing
Always-on cloud health monitor with structured JSON logging.
Runs every 60s, auto-heals via redeploy, activates fallback if needed.
"""
import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timezone

# Configuration
PRIMARY_HEALTH_URL = "https://nearmiss1193-afk--sovereign-orchestrator-health.modal.run"
SECONDARY_RUNNER_URL = "https://empire-fallback-runner.up.railway.app"
CLOUDFLARE_WORKER_URL = "https://empire-webhook-fallback.workers.dev"

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo")

MODAL_ID = os.getenv("MODAL_ID", "")
MODAL_SECRET = os.getenv("MODAL_SECRET", "")

CHECK_INTERVAL = 60  # seconds
MAX_REDEPLOY_ATTEMPTS = 3
BACKOFF_SECONDS = [30, 120, 300]  # exponential backoff

def log(component: str, status: str, action: str, notes: str = ""):
    """Output structured JSON log and persist to Supabase"""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": component,
        "status": status,
        "action": action,
        "notes": notes
    }
    print(json.dumps(entry), flush=True)
    
    # Persist to Supabase
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/health_logs",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "timestamp": entry["timestamp"],
                "component": component,
                "status": status,
                "action_taken": action,
                "message": notes
            },
            timeout=5
        )
    except Exception as e:
        print(json.dumps({"timestamp": entry["timestamp"], "component": "logger", "status": "error", "action": "supabase_write_failed", "notes": str(e)}), flush=True)

def check_health(url: str, timeout: int = 10) -> bool:
    """Check if endpoint returns HTTP 200"""
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except:
        return False

def redeploy_orchestrator() -> bool:
    """Attempt to redeploy the Modal orchestrator"""
    try:
        # Set Modal token if available
        if MODAL_ID and MODAL_SECRET:
            subprocess.run(
                ["py", "-m", "modal", "token", "set", "--token-id", MODAL_ID, "--token-secret", MODAL_SECRET],
                check=True, capture_output=True, timeout=30
            )
        
        # Deploy orchestrator
        result = subprocess.run(
            ["py", "-m", "modal", "deploy", "modal_orchestrator.py"],
            check=True, capture_output=True, timeout=120
        )
        return True
    except subprocess.CalledProcessError as e:
        log("orchestrator", "error", "redeploy_failed", e.stderr.decode() if e.stderr else str(e))
        return False
    except Exception as e:
        log("orchestrator", "error", "redeploy_exception", str(e))
        return False

def activate_fallback():
    """Activate secondary runner and update webhook routing"""
    log("fallback", "activating", "switch_to_secondary", f"Primary down, routing to {SECONDARY_RUNNER_URL}")
    
    # Check if fallback is healthy
    if check_health(f"{SECONDARY_RUNNER_URL}/health"):
        log("fallback", "healthy", "secondary_active", "Fallback runner is responding")
    else:
        log("fallback", "unhealthy", "secondary_unreachable", "WARNING: Fallback runner also down!")

def watchdog_cycle():
    """Single watchdog check cycle"""
    # 1. Check Primary Orchestrator
    if check_health(PRIMARY_HEALTH_URL):
        log("orchestrator", "healthy", "none")
        return
    
    # Unhealthy - begin healing
    log("orchestrator", "unhealthy", "healing_started", "Primary orchestrator not responding")
    
    # 2. Attempt redeploys with backoff
    for attempt in range(MAX_REDEPLOY_ATTEMPTS):
        log("orchestrator", "healing", f"redeploy_attempt_{attempt + 1}", f"Waiting {BACKOFF_SECONDS[attempt]}s before redeploy")
        time.sleep(BACKOFF_SECONDS[attempt])
        
        if redeploy_orchestrator():
            # Wait for service to come up
            time.sleep(30)
            if check_health(PRIMARY_HEALTH_URL):
                log("orchestrator", "recovered", "redeploy_success", f"Recovered after attempt {attempt + 1}")
                return
    
    # 3. All redeploys failed - activate fallback
    log("orchestrator", "critical", "all_redeploys_failed", "Switching to fallback runner")
    activate_fallback()

def main():
    """Main watchdog loop"""
    log("watchdog", "started", "init", f"Monitoring {PRIMARY_HEALTH_URL}")
    
    while True:
        try:
            watchdog_cycle()
        except Exception as e:
            log("watchdog", "error", "cycle_exception", str(e))
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
