"""
MODAL WEBHOOK ONLY - No scheduled functions (avoids cron limit)
Just webhook endpoints for GHL to call
"""
import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi")
app = modal.App("empire-webhooks")
VAULT = modal.Secret.from_name("empire-vault")

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
def inbound_lead(payload: dict):
    """Handle new lead from GHL"""
    import json
    print(f"[INBOUND] New lead: {json.dumps(payload)[:200]}")
    return {"status": "received", "data": payload}

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
def trigger_outreach(payload: dict):
    """Manually trigger outreach"""
    import requests
    import os
    
    email = payload.get("email")
    company = payload.get("company", "Business Owner")
    
    GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"
    
    if email:
        html = f"<p>Hi! Quick question about {company}. We help service businesses capture missed calls with AI. 14-Day Free Trial. Interested? - Daniel, AI Service Co</p>"
        requests.post(GHL_EMAIL, json={
            "email": email,
            "from_name": "Daniel",
            "from_email": "daniel@aiserviceco.com", 
            "subject": f"Quick question for {company}",
            "html_body": html
        }, timeout=15)
        return {"status": "sent", "email": email}
    return {"status": "error", "reason": "no email"}

@app.function(image=image)
@modal.web_endpoint(method="GET")
def health():
    """Health check"""
    from datetime import datetime
    return {"status": "alive", "time": datetime.utcnow().isoformat(), "service": "empire-webhooks"}
