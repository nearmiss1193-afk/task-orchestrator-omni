"""
AGENT: Keep-Alive Heartbeat Trigger
Sends periodic "warm-up" pings to prevent serverless cold starts.
"""
import modal
import requests
import json
import time
from datetime import datetime

app = modal.App("keep-alive-agent")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests")

PRIMARY_ORCHESTRATOR_HEALTH = "https://nearmiss1193-afk--sovereign-orchestrator-health.modal.run"

@app.function(image=image, schedule=modal.Cron("*/5 * * * *"), timeout=60)
def ping_orchestrator():
    start_time = time.time()
    status = "error"
    latency = 0
    
    try:
        r = requests.get(PRIMARY_ORCHESTRATOR_HEALTH, timeout=10)
        latency = int((time.time() - start_time) * 1000)
        
        if r.status_code == 200:
            status = "alive"
        else:
            status = "error"
            
    except Exception as e:
        status = "error"
        # latency remains what it was or 0 if immediate fail
        
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "latency_ms": latency
    }
    
    # Log to stdout (JSON format)
    print(json.dumps(result))
    
    # Return JSON
    return result

@app.local_entrypoint()
def main():
    print(ping_orchestrator.local())
