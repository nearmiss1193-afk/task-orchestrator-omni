"""
MODAL MINIMAL - Super simple cloud deployment
"""
import modal

# Minimal image - just requests
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "requests", "fastapi"
)

app = modal.App("empire-minimal")

VAULT = modal.Secret.from_name("empire-vault")

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(hours=1))
def heartbeat():
    """Simple heartbeat every hour"""
    import requests
    import os
    from datetime import datetime
    
    print(f"[HEARTBEAT] {datetime.utcnow().isoformat()}")
    
    # Send via GHL webhook
    GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"
    
    try:
        requests.post(GHL_EMAIL, json={
            "email": "owner@aiserviceco.com",
            "from_name": "Modal Cloud",
            "from_email": "system@aiserviceco.com",
            "subject": "[CLOUD] Heartbeat - System Running",
            "html_body": f"<p>Modal cloud heartbeat: {datetime.utcnow().isoformat()}</p><p>System is operational.</p>"
        }, timeout=15)
        print("[HEARTBEAT] Email sent")
    except Exception as e:
        print(f"[HEARTBEAT] Error: {e}")
    
    return {"status": "alive", "time": datetime.utcnow().isoformat()}

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="GET")
def health():
    """Health check endpoint"""
    from datetime import datetime
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    print("Deploy: python -m modal deploy deploy_minimal.py")
