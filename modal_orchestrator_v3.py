"""
SOVEREIGN ORCHESTRATOR - Stripped down for emergency recovery
Only essential endpoints, NO scheduled functions
"""
import modal
from fastapi import FastAPI, Request
from datetime import datetime
import json
import os

image = modal.Image.debian_slim(python_version="3.11").pip_install("fastapi[standard]", "requests")

# Define secrets - these MUST be set via `modal secret create`
secrets = modal.Secret.from_name("empire-secrets")

app = modal.App("empire-api-v3", image=image, secrets=[secrets])

# Config (Non-sensitive constants only)
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
BOOKING_LINK = "https://link.aiserviceco.com/discovery"
ESCALATION_PHONE = "+13529368152"

# Secrets loaded at runtime from modal.Secret
def get_secrets():
    return {
        "SUPABASE_KEY": os.environ.get("SUPABASE_KEY", ""),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
        "RESEND_API_KEY": os.environ.get("RESEND_API_KEY", "")
    }

@app.function()
@modal.asgi_app()
def orchestration_api():
    api = FastAPI(title="Sovereign Orchestrator v3 (Emergency)")
    
    import requests
    secrets = get_secrets()
    SUPABASE_KEY = secrets["SUPABASE_KEY"]
    
    def log_event(event_type: str, source: str, severity: str = "info", 
                  correlation_id: str = None, entity_id: str = None, payload: dict = None):
        """Log event to Supabase event_log_v2"""
        try:
            event = {
                "type": event_type,
                "source": source,
                "severity": severity,
                "correlation_id": correlation_id,
                "entity_id": entity_id,
                "payload": payload or {},
                "ts": datetime.utcnow().isoformat()
            }
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            requests.post(f"{SUPABASE_URL}/rest/v1/event_log_v2", headers=headers, json=event, timeout=10)
        except Exception as e:
            print(f"[Log Error] {e}")
    
    @api.get("/health")
    def health():
        """Health check endpoint"""
        return {
            "status": "ok",
            "orchestrator": "sovereign-v3-emergency",
            "agents": ["sarah", "christina"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.get("/api/kpi-snapshot")
    def kpi_snapshot():
        """Emit KPI snapshot - simplified"""
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Prefer": "count=exact"}
            leads_resp = requests.get(f"{SUPABASE_URL}/rest/v1/contacts_master?select=count", headers=headers)
            lead_count = int(leads_resp.headers.get("content-range", "0-0/0").split("/")[-1])
            
            kpi_data = {
                "leads_total": lead_count,
                "bookings_total": 0,
                "booking_rate": 0.0,
                "version": "v3-emergency"
            }
            
            log_event("kpi.snapshot", "modal", "info", payload=kpi_data)
            return {"status": "ok", "kpi": kpi_data}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @api.get("/api/reliability-check")
    def reliability_check():
        """Basic reliability check"""
        from datetime import timedelta
        
        checks = {}
        utc_now = datetime.utcnow()
        ct_now = utc_now - timedelta(hours=6)
        today = ct_now.strftime('%Y-%m-%d')
        
        # DB connectivity
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            test_resp = requests.get(f"{SUPABASE_URL}/rest/v1/event_log_v2?limit=1", headers=headers, timeout=5)
            checks["database"] = "ok" if test_resp.status_code == 200 else "error"
        except:
            checks["database"] = "error"
        
        # Outreach enabled
        outreach_enabled = os.environ.get("OUTREACH_ENABLED", "true").lower() == "true"
        checks["outreach_enabled"] = outreach_enabled
        
        return {
            "status": "healthy" if checks.get("database") == "ok" else "degraded",
            "checks": checks,
            "ct_time": ct_now.strftime('%Y-%m-%d %H:%M:%S'),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.get("/api/kickoff-status") 
    def kickoff_status():
        """Returns kickoff readiness status for Jan 18 launch"""
        from datetime import timedelta
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        
        utc_now = datetime.utcnow()
        ct_now = utc_now - timedelta(hours=6)
        today = ct_now.strftime('%Y-%m-%d')
        tomorrow = (ct_now + timedelta(days=1)).strftime('%Y-%m-%d')
        
        kickoff_scheduled = False
        kickoff_executed = False
        kickoff_date = None
        
        try:
            # Check today and tomorrow's kickoff
            for check_date in [today, tomorrow]:
                kr_resp = requests.get(
                    f"{SUPABASE_URL}/rest/v1/kickoff_runs?date=eq.{check_date}&limit=1",
                    headers=headers, timeout=10
                )
                if kr_resp.status_code == 200 and kr_resp.json():
                    row = kr_resp.json()[0]
                    kickoff_scheduled = True
                    kickoff_executed = row.get("executed", False)
                    kickoff_date = row.get("date")
                    break
        except Exception as e:
            print(f"[Kickoff Status] Error: {e}")
        
        # Count active variants
        active_variants = 0
        try:
            v_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/prompt_variants?active=eq.true&vertical=eq.hvac",
                headers=headers, timeout=10
            )
            if v_resp.status_code == 200:
                active_variants = len(v_resp.json())
        except:
            pass
        
        outreach_enabled = os.environ.get("OUTREACH_ENABLED", "true").lower() == "true"
        readiness = "GO" if (kickoff_scheduled and active_variants > 0 and outreach_enabled) else "NOT_READY"
        
        return {
            "status": "ok",
            "today": today,
            "tomorrow": tomorrow,
            "kickoff_scheduled_for_tomorrow": kickoff_scheduled,
            "kickoff_date": kickoff_date,
            "kickoff_executed": kickoff_executed,
            "active_variants_count": active_variants,
            "outreach_enabled": outreach_enabled,
            "ct_time": ct_now.strftime('%Y-%m-%d %H:%M:%S CT'),
            "readiness": readiness,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @api.post("/api/campaign-batch")
    def campaign_batch(data: dict):
        """Execute batch campaign for contacts"""
        import time
        import uuid
        
        # Outreach kill switch
        outreach_enabled = os.environ.get("OUTREACH_ENABLED", "true").lower() == "true"
        if not outreach_enabled:
            log_event("campaign.disabled", "modal", "warn", payload={
                "reason": "OUTREACH_ENABLED=false",
                "contact_count": len(data.get("contacts", []))
            })
            return {
                "status": "disabled",
                "reason": "OUTREACH_ENABLED=false",
                "sent": 0, "skipped_window": 0, "failed": 0, "details": []
            }
        
        contacts = data.get("contacts", [])
        dry_run = data.get("dry_run", False)
        run_id = data.get("run_id") or f"batch_{uuid.uuid4().hex[:8]}"
        
        results = {"sent": 0, "skipped_window": 0, "failed": 0, "details": []}
        
        log_event("campaign.batch.started", "modal", "info", correlation_id=run_id, payload={
            "contact_count": len(contacts),
            "dry_run": dry_run
        })
        
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        for contact in contacts[:50]:  # Limit to 50 per batch
            phone = contact.get("phone", "")
            company = contact.get("company", "")
            vertical = contact.get("vertical", "hvac")
            
            try:
                if dry_run:
                    results["sent"] += 1
                    results["details"].append({"phone": phone, "status": "dry_run", "company": company})
                else:
                    # Send via GHL webhook
                    ghl_resp = requests.post(GHL_SMS_WEBHOOK, json={
                        "phone": phone,
                        "message": f"Hi! We have a free diagnostic report ready for {company}. Reply YES to receive it, or STOP to opt out."
                    }, timeout=30)
                    
                    if ghl_resp.status_code in [200, 201]:
                        results["sent"] += 1
                        results["details"].append({"phone": phone, "status": "sent", "company": company})
                        log_event("sms.outbound", "modal", "info", entity_id=phone, payload={
                            "company": company, "vertical": vertical, "run_id": run_id
                        })
                    else:
                        results["failed"] += 1
                        results["details"].append({"phone": phone, "status": "ghl_error", "code": ghl_resp.status_code})
            except Exception as e:
                results["failed"] += 1
                results["details"].append({"phone": phone, "status": "exception", "error": str(e)})
            
            time.sleep(0.5)  # Rate limiting
        
        log_event("campaign.batch.completed", "modal", "info", correlation_id=run_id, payload={
            "sent": results["sent"],
            "failed": results["failed"],
            "dry_run": dry_run
        })
        
        return {
            "status": "ok",
            "run_id": run_id,
            "sent": results["sent"],
            "skipped_window": results["skipped_window"],
            "failed": results["failed"],
            "details": results["details"][:20]
        }
    
    @api.get("/api/learning-status")
    def learning_status():
        """Dashboard endpoint: Get current learning status"""
        return {
            "status": "ok",
            "policy": {"version": 3, "max_retries": 3, "weight_gemini": 0.7},
            "variants": [],
            "incidents": [],
            "canaries": []
        }
    
    return api
