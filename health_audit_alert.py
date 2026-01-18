"""
AUTOMATED HEALTH AUDIT + STORAGE + ALERT
Evaluates all critical components, stores to Supabase, dispatches alerts on failures.
"""
import os
import json
import requests
from datetime import datetime, timezone

# Configuration
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

# Endpoints
ORCHESTRATOR_PROD = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health"
ORCHESTRATOR_DEV = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/optimize"
FALLBACK_RUNNER = "https://empire-fallback-runner.up.railway.app/health"
CLOUDFLARE_WORKER = "https://empire-webhook-fallback.workers.dev"

# Alert channels
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
ALERT_PHONE = "+13529368152"
ALERT_EMAIL = "nearmiss1193@gmail.com"

def check_endpoint(url, timeout=15):
    try:
        r = requests.get(url, timeout=timeout)
        return {"status": r.status_code, "ok": r.status_code == 200, "body": r.text[:100]}
    except Exception as e:
        return {"status": 0, "ok": False, "body": str(e)[:100]}

def log_to_supabase(component, status, action, message=""):
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/health_logs",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"},
            json={"timestamp": datetime.now(timezone.utc).isoformat(), "component": component, "status": status, "action_taken": action, "message": message},
            timeout=10
        )
    except:
        pass

def send_alert(message, channel="sms"):
    """Send alert via GHL webhook"""
    try:
        requests.post(GHL_SMS_WEBHOOK, json={
            "phone": ALERT_PHONE,
            "email": ALERT_EMAIL,
            "message": f"🚨 EMPIRE ALERT: {message}",
            "subject": "Empire System Alert"
        }, timeout=15)
        return True
    except:
        return False

def run_health_audit():
    timestamp = datetime.now(timezone.utc).isoformat()
    alerts_to_send = []
    
    # 1. Check Orchestrator
    prod = check_endpoint(ORCHESTRATOR_PROD)
    dev = check_endpoint(ORCHESTRATOR_DEV)
    orchestrator_status = "healthy" if prod["ok"] else ("degraded" if dev["ok"] else "failed")
    log_to_supabase("orchestrator", orchestrator_status, "health_check", f"prod:{prod['status']} dev:{dev['status']}")
    if not prod["ok"] and not dev["ok"]:
        alerts_to_send.append("Orchestrator DOWN - both prod and dev endpoints failing")
    
    # 2. Check Fallback Runner
    fallback = check_endpoint(FALLBACK_RUNNER)
    fallback_status = "healthy" if fallback["ok"] else "unhealthy"
    log_to_supabase("fallback_runner", fallback_status, "health_check", fallback["body"])
    if not fallback["ok"]:
        alerts_to_send.append("Fallback Runner unreachable")
    
    # 3. Check Cloudflare Worker
    cf = check_endpoint(CLOUDFLARE_WORKER)
    cf_status = "deployed" if cf["status"] in [200, 405] else "error"
    log_to_supabase("cloudflare_webhook", cf_status, "health_check", cf["body"])
    if cf["status"] not in [200, 405]:
        alerts_to_send.append("Cloudflare Worker not deployed")
    
    # 4. Check Supabase logs
    try:
        h = {"apikey": SUPABASE_KEY, "Prefer": "count=exact"}
        hl = requests.get(f"{SUPABASE_URL}/rest/v1/health_logs?select=count", headers=h, timeout=10)
        supabase_ok = hl.status_code == 200
    except:
        supabase_ok = False
    log_to_supabase("supabase", "healthy" if supabase_ok else "error", "connectivity_check")
    
    # 5. Send alerts if needed
    alerts_sent = []
    for alert_msg in alerts_to_send:
        if send_alert(alert_msg):
            alerts_sent.append({"message": alert_msg, "channel": "sms", "sent": True})
        else:
            alerts_sent.append({"message": alert_msg, "channel": "sms", "sent": False})
    
    # Summary
    overall = "healthy"
    if len(alerts_to_send) > 0:
        overall = "action_required"
    elif not prod["ok"]:
        overall = "degraded"
    
    report = {
        "timestamp": timestamp,
        "orchestrator": {
            "prod_endpoint": "healthy" if prod["ok"] else "failed",
            "dev_endpoint": "healthy" if dev["ok"] else "failed",
            "prod_status": prod["status"],
            "dev_status": dev["status"]
        },
        "fallback_runner": {
            "status": fallback_status,
            "http_status": fallback["status"]
        },
        "cloudflare_webhook": {
            "status": cf_status,
            "http_status": cf["status"]
        },
        "supabase_logging": {
            "status": "healthy" if supabase_ok else "error"
        },
        "alerts_sent": alerts_sent,
        "summary": {
            "overall_status": overall,
            "critical_issues": len(alerts_to_send),
            "recommendations": []
        }
    }
    
    if not prod["ok"]:
        report["summary"]["recommendations"].append("DEPLOY ORCHESTRATOR: python -m modal deploy modal_orchestrator.py")
    if not fallback["ok"]:
        report["summary"]["recommendations"].append("DEPLOY RAILWAY: railway login && railway up")
    if cf["status"] not in [200, 405]:
        report["summary"]["recommendations"].append("DEPLOY CLOUDFLARE: npx wrangler deploy")
    
    return report

if __name__ == "__main__":
    result = run_health_audit()
    print(json.dumps(result, indent=2))
