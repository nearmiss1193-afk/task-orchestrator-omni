"""
MODAL CLOUD MONITOR - Self-healing orchestrator monitor deployed to Modal
Runs 24/7 on Modal cloud, monitors health and auto-redeploys
"""
import modal
from datetime import datetime
import time

app = modal.App("orchestrator-monitor")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests", "fastapi")

ORCHESTRATOR_HEALTH_URL = "https://nearmiss1193-afk--sovereign-orchestrator-health.modal.run"
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"


@app.function(image=image, schedule=modal.Cron("*/5 * * * *"), timeout=120)
def monitor_health():
    """Check orchestrator health every 5 minutes"""
    import requests
    
    print(f"[{datetime.utcnow().isoformat()}] Health check starting...")
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    try:
        r = requests.get(ORCHESTRATOR_HEALTH_URL, timeout=10)
        status = "healthy" if r.status_code == 200 else f"unhealthy_{r.status_code}"
        
        # Log to Supabase
        requests.post(f"{SUPABASE_URL}/rest/v1/event_log", headers=headers, json={
            "event_type": "health_check",
            "success": r.status_code == 200,
            "details": {"status": status, "url": ORCHESTRATOR_HEALTH_URL}
        })
        
        print(f"  Status: {status}")
        return {"status": status, "timestamp": datetime.utcnow().isoformat()}
        
    except Exception as e:
        # Log failure
        requests.post(f"{SUPABASE_URL}/rest/v1/event_log", headers=headers, json={
            "event_type": "health_check_failed",
            "success": False,
            "details": {"error": str(e)}
        })
        print(f"  ERROR: {e}")
        return {"status": "error", "error": str(e)}


@app.function(image=image, schedule=modal.Cron("*/10 * * * *"), timeout=300)
def run_campaign_touch():
    """Run campaign touches every 10 minutes"""
    import requests
    
    print(f"[{datetime.utcnow().isoformat()}] Campaign touch check...")
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
    BOOKING_LINK = "https://link.aiserviceco.com/discovery"
    
    # Get leads needing touch 1
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads?status=eq.new&limit=5",
        headers=headers
    )
    leads = r.json() if r.status_code == 200 else []
    
    sent = 0
    for lead in leads:
        phone = lead.get("phone")
        name = lead.get("name", "there")
        company = lead.get("company_name", "your business")
        
        if not phone:
            continue
        
        # Check business hours (simple UTC check 13:00-22:00 UTC = 8am-5pm ET)
        hour = datetime.utcnow().hour
        if hour < 13 or hour >= 22:
            print(f"  Skipping {name} - outside business hours")
            continue
        
        # Send SMS
        msg = f"Hi {name}! I'm Christina from AI Service Co. Quick wins for {company}: {BOOKING_LINK}"
        
        try:
            sms_r = requests.post(GHL_SMS_WEBHOOK, json={"phone": phone, "message": msg}, timeout=15)
            
            if sms_r.status_code == 200:
                # Update lead status
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}",
                    headers=headers,
                    json={"status": "contacted", "disposition": "sent_link"}
                )
                sent += 1
                print(f"  ✅ Sent to {name}")
            
            time.sleep(2)  # Rate limit
            
        except Exception as e:
            print(f"  ❌ Failed for {name}: {e}")
    
    print(f"  Total sent: {sent}")
    return {"sent": sent, "timestamp": datetime.utcnow().isoformat()}


@app.function(image=image, timeout=30)
@modal.web_endpoint(method="GET")
def health():
    """Monitor health endpoint"""
    return {
        "status": "ok",
        "service": "orchestrator-monitor",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.local_entrypoint()
def main():
    print("Orchestrator Monitor deployed!")
    print("Scheduled jobs:")
    print("  - monitor_health: every 5 minutes")
    print("  - run_campaign_touch: every 10 minutes")
