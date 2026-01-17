"""
SOVEREIGN ORCHESTRATOR LITE - Simplified for debugging
"""
import modal
from datetime import datetime

app = modal.App("empire-orchestrator")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi")


@app.function(image=image, timeout=60)
@modal.web_endpoint(method="POST")
def handle_inbound(data: dict):
    """Handle inbound SMS/call"""
    return {"agent": "sarah", "received": True, "timestamp": datetime.utcnow().isoformat()}


@app.function(image=image, timeout=60)
@modal.web_endpoint(method="POST")
def handle_outbound(data: dict):
    """Handle outbound campaign"""
    return {"agent": "christina", "received": True, "timestamp": datetime.utcnow().isoformat()}


@app.function(image=image, timeout=30)
@modal.web_endpoint(method="GET")
def health():
    """Health check endpoint"""
    return {"status": "ok", "orchestrator": "sovereign", "agents": ["sarah", "christina"], "timestamp": datetime.utcnow().isoformat()}
