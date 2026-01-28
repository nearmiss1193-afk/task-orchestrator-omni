import os
import requests
from dotenv import load_dotenv

load_dotenv()

GHL_WEBHOOK_URL = os.getenv("GHL_EMAIL_WEBHOOK_URL")

def send_summary():
    print("📧 Sending Session Summary...")
    
    summary = """
    📊 SESSION SUMMARY - 2026-01-27

    **Completed:**
    - Standardized Sarah AI (Vapi) for 'Manus Direct' (Personalized Audit Hook)
    - Synchronized Sarah Assistant IDs (Ending in 8539a)
    - Enforced Modal Free Tier Hardening (8-function limit)
    - Standardized Modal Scoping/Logging (_brain_log)
    - Enforced Contact Hours for Calls (8am-6pm EST)
    - Added Vapi Feedback Webhook (/vapi-webhook)
    - Implemented Cloud-Run Rule (Autonomous Mode)

    **Active Systems:**
    - Campaign Status: Running (Modal)
    - Sarah AI: Active ( manus-direct-hook)
    - Modal Cloud: ✅ Deployed (nexus-outreach-v1)
    - GHL Integration: ✅ Webhooks LIVE
    - Supabase: ✅ Connection Stable (115 leads)

    **Git Commits:**
    - dfed522 - SAVE PROTOCOL: Manus Direct readiness, Modal hardening (8-func limit), Sarah AI optimization
    """
    
    payload = {
        "contact_id": "OAD-3b01-4675-9bd8-b8820981c171", # Dashboard Owner
        "email": "nearmiss1193@gmail.com",
        "subject": "📊 SESSION SUMMARY - Manus Direct Optimized",
        "body": summary
    }
    
    try:
        res = requests.post(GHL_WEBHOOK_URL, json=payload)
        if res.status_code in [200, 201, 204]:
            print("✅ Summary sent to nearmiss1193@gmail.com")
        else:
            print(f"❌ Failed to send summary: {res.text}")
    except Exception as e:
        print(f"❌ Summary Error: {e}")

if __name__ == "__main__":
    send_summary()
