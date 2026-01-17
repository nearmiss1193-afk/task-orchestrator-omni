"""
SOVEREIGN ORCHESTRATOR - HEALTH ENDPOINT
Single-function app for reliable deployment
"""
import modal
from datetime import datetime

app = modal.App("orch-health")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi")

@app.function(image=image, timeout=30)
@modal.web_endpoint(method="GET")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "orchestrator": "sovereign",
        "agents": ["sarah", "christina"],
        "timestamp": datetime.utcnow().isoformat()
    }
