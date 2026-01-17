import base64
import os

print("Reading modal_orchestrator.py...")
with open("modal_orchestrator.py", "rb") as f:
    orch_bytes = f.read()

orch_b64 = base64.b64encode(orch_bytes).decode('utf-8')

# Check for local credentials
local_id = os.getenv("MODAL_ID", "")
local_secret = os.getenv("MODAL_SECRET", "")

print(f"Found local credentials? ID={'Yes' if local_id else 'No'}")

template = r'''"""
ORCHESTRATOR FAULT-TOLERANCE (Self-Healing)
"""
import os
import requests
import subprocess
import base64
import modal
from datetime import datetime

# --- Config ---
PRIMARY_HEALTH = "https://nearmiss1193-afk--sovereign-orchestrator-health.modal.run"
SECONDARY_WEBHOOK_URL = "https://your-fallback-url.fly.dev/webhook"
GHL_WEBHOOK_REGISTRATION = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

ORCH_B64 = "__ORCH_B64__"
INJECTED_ID = "__INJECTED_ID__"
INJECTED_SECRET = "__INJECTED_SECRET__"

app = modal.App("orchestrator-fault-tolerance")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi", "modal")

def log_health(status, action, notes=""):
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/system_health",
            headers=HEADERS,
            json={
                "check_time": datetime.utcnow().isoformat(),
                "orchestrator_up": status == "healthy",
                "notes": f"{action} | {notes}"
            },
            timeout=5
        )
    except:
        pass

def restore_file():
    with open("modal_orchestrator.py", "wb") as f:
        f.write(base64.b64decode(ORCH_B64))

def switch_to_fallback():
    try:
        requests.post(GHL_WEBHOOK_REGISTRATION, json={"url": SECONDARY_WEBHOOK_URL}, timeout=10)
        log_health("unhealthy", "fallback_active", f"Switched to {SECONDARY_WEBHOOK_URL}")
    except Exception as e:
        log_health("unhealthy", "fallback_failed", str(e))

def redeploy():
    restore_file()
    token_id = INJECTED_ID or os.getenv("MODAL_ID")
    token_secret = INJECTED_SECRET or os.getenv("MODAL_SECRET")
    
    if token_id and token_secret:
        subprocess.run(["python", "-m", "modal", "token", "set", "--token-id", token_id, "--token-secret", token_secret], check=True)
    
    # Deploy sovereign-orchestrator
    subprocess.run(["python", "-m", "modal", "deploy", "modal_orchestrator.py", "--name", "sovereign-orchestrator"], check=True)
    return True

@app.function(image=image, schedule=modal.Cron("*/5 * * * *"), timeout=300)
def monitor():
    print("Checking health...")
    try:
        r = requests.get(PRIMARY_HEALTH, timeout=10)
        if r.status_code == 200:
            status = r.json()
            if status.get("status") == "ok":
                log_health("healthy", "none")
                return
    except:
        pass
    
    print("Unhealthy! Redeploying...")
    log_health("unhealthy", "redeploy")
    try:
        redeploy()
        log_health("healthy", "redeploy_success")
    except Exception as e:
        print(f"Redeploy failed: {e}")
        log_health("degraded", "redeploy_failed", str(e))
        switch_to_fallback()

@app.local_entrypoint()
def main():
    monitor.local()
'''

content = template.replace("__ORCH_B64__", orch_b64)
content = content.replace("__INJECTED_ID__", local_id)
content = content.replace("__INJECTED_SECRET__", local_secret)

with open("orchestrator_fault_tolerance.py", "w") as f:
    f.write(content)
print("Done.")
