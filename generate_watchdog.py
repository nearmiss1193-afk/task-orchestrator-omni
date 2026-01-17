import base64
import os

print("Reading modal_orchestrator.py...")
with open("modal_orchestrator.py", "rb") as f:
    orch_bytes = f.read()
orch_b64 = base64.b64encode(orch_bytes).decode('utf-8')

# Check for local credentials
local_id = os.getenv("MODAL_ID", "")
local_secret = os.getenv("MODAL_SECRET", "")

template = r'''"""
AGENT: WATCHDOG — Cloud Health Monitor & Self-Healing
"""
import os
import requests
import subprocess
import base64
import modal
import time
from datetime import datetime

# --- Targets ---
TARGETS = {
    "PRIMARY_ORCHESTRATOR": "https://nearmiss1193-afk--sovereign-orchestrator-health.modal.run",
    "INBOUND_WEBHOOK": "https://nearmiss1193-afk--webhook-server-health.modal.run",
    "CAMPAIGN_SCHEDULER": "https://nearmiss1193-afk--orchestrator-monitor-health.modal.run"
}
FALLBACK_URL = "https://your-fallback-url.fly.dev"

# --- Config ---
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

ORCH_B64 = "__ORCH_B64__"
INJECTED_ID = "__INJECTED_ID__"
INJECTED_SECRET = "__INJECTED_SECRET__"

app = modal.App("cloud-watchdog")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "modal")

def log(component, status, action, notes=""):
    print(f"[{datetime.utcnow().isoformat()}] {component}: {status} - {action} ({notes})")
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/system_health",
            headers=HEADERS,
            json={
                "check_time": datetime.utcnow().isoformat(),
                "orchestrator_up": status == "healthy", # Generic flag
                "notes": f"[{component}] {status}: {action} | {notes}"
            },
            timeout=5
        )
    except Exception as e:
        print(f"Log failed: {e}")

def restore_files():
    with open("modal_orchestrator.py", "wb") as f:
        f.write(base64.b64decode(ORCH_B64))

def redeploy_orchestrator():
    restore_files()
    token_id = INJECTED_ID or os.getenv("MODAL_ID")
    token_secret = INJECTED_SECRET or os.getenv("MODAL_SECRET")
    
    if token_id and token_secret:
        subprocess.run(["python", "-m", "modal", "token", "set", "--token-id", token_id, "--token-secret", token_secret], check=True)
    
    subprocess.run(["python", "-m", "modal", "deploy", "modal_orchestrator.py", "--name", "sovereign-orchestrator"], check=True)
    return True

@app.function(image=image, schedule=modal.Cron("*/1 * * * *"), timeout=300)
def watchdog_check():
    print("--- WATCHDOG CHECK ---")
    
    # 1. Check Primary Orchestrator
    try:
        r = requests.get(TARGETS["PRIMARY_ORCHESTRATOR"], timeout=10)
        if r.status_code == 200:
            log("PRIMARY_ORCHESTRATOR", "healthy", "none")
        else:
            raise Exception(f"Status {r.status_code}")
    except Exception as e:
        log("PRIMARY_ORCHESTRATOR", "unhealthy", "healing", str(e))
        try:
            redeploy_orchestrator()
            log("PRIMARY_ORCHESTRATOR", "healing", "redeploy_success")
        except Exception as redeploy_err:
            log("PRIMARY_ORCHESTRATOR", "critical", "redeploy_failed", str(redeploy_err))

    # 2. Check Webhook Listener
    try:
        r = requests.get(TARGETS["INBOUND_WEBHOOK"], timeout=10)
        if r.status_code == 200:
            log("INBOUND_WEBHOOK", "healthy", "none")
        else:
            log("INBOUND_WEBHOOK", "unhealthy", "check_deployment")
    except Exception as e:
        log("INBOUND_WEBHOOK", "down", "check_cloud", str(e))

    # 3. Check Campaign Scheduler
    try:
        r = requests.get(TARGETS["CAMPAIGN_SCHEDULER"], timeout=10)
        if r.status_code == 200:
            log("CAMPAIGN_SCHEDULER", "healthy", "none")
        else:
            log("CAMPAIGN_SCHEDULER", "unhealthy", "unknown")
    except Exception as e:
         log("CAMPAIGN_SCHEDULER", "down", "unknown", str(e))

@app.local_entrypoint()
def main():
    watchdog_check.local()
'''

content = template.replace("__ORCH_B64__", orch_b64)
content = content.replace("__INJECTED_ID__", local_id)
content = content.replace("__INJECTED_SECRET__", local_secret)

with open("cloud_watchdog.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Generated cloud_watchdog.py with UTF-8 encoding")
