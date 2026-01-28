import os
import requests
from dotenv import load_dotenv

load_dotenv()

GHL_WEBHOOK_URL = os.getenv("GHL_EMAIL_WEBHOOK_URL")

def send_summary():
    print("📧 Sending Session Summary...")
    
    summary = """
    📊 SESSION SUMMARY - 2026-01-28 (THE GREAT REFACTOR)

    **Completed:**
    - Modularized deploy.py into core/workers/api structure (Reduced to <50 lines)
    - Implemented Strict Error Hardening (No more silent DB/Webhook failures)
    - Applied Grok-3 Throttling (Protected Supabase 100k write limit)
    - Implemented Daily Call Cap (20 calls/day for Sarah)
    - Verified 100% Cloud Stability & Heartbeat
    - Sarah Voice optimization settings received from Grok-3

    **Active Systems:**
    - Campaign Status: Running (Throttled/Hardened)
    - Sarah AI: Active (8am-6pm EST calling window)
    - Modal Cloud: ✅ Deployed (nexus-outreach-v1)
    - GHL Integration: ✅ Webhooks LIVE
    - Supabase: ✅ Connection Stable

    **Next Priority:**
    - Monitor throttled throughput for 24h
    - Finalize Vapi voice update (once auth key is refreshed)
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
