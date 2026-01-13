import modal
import requests
import os

app = modal.App("empire-watchdog")

# Config
RAILWAY_URL = "https://empire-unified-backup-production.up.railway.app/health"
BACKUP_PHONE = "+13529368152"
GHL_SMS_WEBHOOK = "https://empire-unified-backup-production.up.railway.app/ghl/inbound-sms" 
# Note: If Railway is down, GHL hook fails too. We should use a direct Twilio/GHL fallthrough if possible,
# or assume GHL itself is up and we can hit their direct API, but for now we'll log/print.
# A true failover needs a 3rd party sender (like simple Twilio direct).

image = modal.Image.debian_slim().pip_install("requests")

@app.function(schedule=modal.Cron("*/5 * * * *"), image=image)
def check_health():
    print(f"Checking {RAILWAY_URL}...")
    try:
        r = requests.get(RAILWAY_URL, timeout=10)
        if r.status_code == 200:
            print("✅ Railway System Operational")
            return
        else:
            print(f"❌ Railway Health Check Failed: {r.status_code}")
            alert_down(f"Status Code: {r.status_code}")
    except Exception as e:
        print(f"❌ Railway Connection Failed: {e}")
        alert_down(f"Connection Error: {e}")

def alert_down(reason):
    print(f"CRITICAL ALERT: System Down! Reason: {reason}")
    # TODO: Integrate Twilio or SendGrid direct here for 3rd layer redundancy
    # For now, we print to logs which are visible in Modal dashboard
