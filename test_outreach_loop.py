import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# Configuration
TEST_CONTACT_ID = "ghl_test_123"
TEST_PHONE = os.getenv("TEST_PHONE", "+13529368152")
TEST_EMAIL = os.getenv("TEST_EMAIL", "nearmiss1193@gmail.com")
ORCHESTRATOR_URL = "https://nearmiss1193-afk--nexus-outreach-v1-orchestration-api.modal.run" # Modal direct URL

def run_smoke_test():
    print("🚀 Starting Manus Direct Smoke Test Loop...")
    
    # Stage 1: Verify Webhook Connectivity
    print("\n[1/3] Verifying Webhook Connectivity...")
    try:
        res = requests.get(f"{ORCHESTRATOR_URL}/health")
        if res.status_code == 200:
            print("✅ Orchestrator Health OK")
        else:
            print(f"❌ Orchestrator Health Fail: {res.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # Stage 2: Trigger Simulated Email Open
    print("\n[2/3] Triggering Simulated Email Open (Webhook Trigger)...")
    webhook_payload = {
        "contact_id": TEST_CONTACT_ID,
        "email": TEST_EMAIL,
        "event_type": "email_opened"
    }
    
    try:
        # Note: In production, the Vercel proxy aiserviceco.com/api/webhook/email-opened handles this
        res = requests.post(f"{ORCHESTRATOR_URL}/api/webhook/email-opened", json=webhook_payload)
        if res.status_code == 200:
            print(f"✅ Webhook Triggered: {res.json().get('message')}")
        else:
            print(f"❌ Webhook Fail: {res.status_code} - {res.text}")
            return
    except Exception as e:
        print(f"❌ Webhook Exception: {e}")
        return

    # Stage 3: Verify Sarah is Dialing
    print("\n[3/3] VERIFICATION: Sarah should be calling your phone now...")
    print(f"📱 Calling: {TEST_PHONE}")
    print("Check your phone. If Sarah picks up with the 'Manus Direct' hook, we are LIVE.")

if __name__ == "__main__":
    run_smoke_test()
