"""
MODAL LIGHT - Split deployment for reliability
Just the core operations: Prospecting, Outreach, Responder
"""
import modal
import os

# Lightweight image
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "requests", "supabase", "python-dotenv", "fastapi", "pytz"
)

app = modal.App("empire-core")

# Secrets
VAULT = modal.Secret.from_name("empire-vault")

# ============ CORE FUNCTIONS ============

@app.function(image=image, secrets=[VAULT], schedule=modal.Period(hours=2))
def prospect_loop():
    """Find new leads every 2 hours"""
    import requests
    import os
    
    print("[MODAL] Starting prospect loop...")
    
    apollo_key = os.environ.get("APOLLO_API_KEY")
    if not apollo_key:
        print("[MODAL] Missing APOLLO_API_KEY")
        return {"status": "error", "reason": "no_key"}
    
    niches = ["HVAC contractors Florida", "Plumbing services Texas", "Roofing companies Georgia"]
    leads_found = 0
    
    for niche in niches:
        try:
            resp = requests.post(
                "https://api.apollo.io/v1/mixed_companies/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": apollo_key,
                    "q_keywords": niche,
                    "per_page": 10,
                    "organization_num_employees_ranges": ["1,10", "11,50"]
                },
                timeout=30
            )
            if resp.ok:
                data = resp.json()
                companies = data.get("organizations", [])
                leads_found += len(companies)
                print(f"[MODAL] Found {len(companies)} for {niche}")
        except Exception as e:
            print(f"[MODAL] Apollo error: {e}")
    
    return {"status": "ok", "leads_found": leads_found}


@app.function(image=image, secrets=[VAULT], schedule=modal.Period(hours=1))
def outreach_loop():
    """Send outreach every hour (8am-6pm ET)"""
    import requests
    import os
    from datetime import datetime
    import pytz
    
    print("[MODAL] Starting outreach loop...")
    
    # Time gate: Only run 8am-6pm ET
    et = pytz.timezone("US/Eastern")
    now = datetime.now(et)
    if not (8 <= now.hour < 18):
        print(f"[MODAL] Outside business hours ({now.hour}:00 ET)")
        return {"status": "skipped", "reason": "outside_hours"}
    
    # GHL Webhooks
    GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"
    GHL_SMS = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
    
    # For now, just log that we're running
    # In full version, this would pull from Supabase and send outreach
    print("[MODAL] Outreach ready - checking for leads...")
    
    return {"status": "ok", "time": now.isoformat()}


@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
def ghl_webhook(payload: dict):
    """Handle inbound GHL webhooks"""
    import json
    
    print(f"[MODAL] Webhook received: {json.dumps(payload)[:200]}")
    
    msg_type = payload.get("type", "unknown")
    contact_id = payload.get("contactId") or payload.get("contact_id")
    
    return {
        "status": "received",
        "type": msg_type,
        "contact_id": contact_id
    }


@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="GET")
def health():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "empire-core",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    print("Deploy with: python -m modal deploy deploy_light.py")
