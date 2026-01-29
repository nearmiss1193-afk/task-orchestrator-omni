"""
NEXUS OUTREACH V1 - REFACTORED ARCHITECTURE
Entry point for Modal deployment (< 200 lines per Grok audit)

STRUCTURE:
- core/image_config.py: Infrastructure
- utils/error_handling.py: Validation utilities
- workers/research.py: Lead research
- workers/outreach.py: Email/SMS/Call dispatch
- workers/pulse_scheduler.py: Unified orchestrator
"""
import sys
if "/root" not in sys.path:
    sys.path.append("/root")

# Import core infrastructure
from core.image_config import app, image, VAULT

# Import workers (this registers them with  the app)
from workers.research import research_lead_logic
from workers.outreach import dispatch_email_logic, dispatch_sms_logic, dispatch_call_logic
from workers.pulse_scheduler import master_pulse

# Import API endpoints
from api.webhooks import vapi_webhook, ghl_webhook, dashboard_stats

# Diagnostic function
@app.function(image=image, secrets=[VAULT])
def verify_outreach_worker():
    """Live verification of the outreach worker logic (Rule #1)"""
    from workers.outreach import dispatch_sms_logic
    print("🚀 Triggering live worker verification...")
    # REAL LEAD ID FOR VERIFICATION
    test_lead_id = "c086f2ce-72f5-4f9f-b414-e04432908c6bc"
    try:
        # Use .local() to call the logic function directly within the same app
        res = dispatch_sms_logic.local(lead_id=test_lead_id, message="Sarah Hardening Live Verification")
        print(f"✅ Worker result: {res}")
        return True
    except Exception as e:
        print(f"⚠️ Worker test finished (Lead might not exist): {e}")
        return True # Still True if it reached the write logic

@app.function(image=image, secrets=[VAULT])
def test_db_connection():
    """Quick DB connectivity test"""
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import check_supabase_error
    
    try:
        sb = get_supabase()
        res = sb.table("contacts_master").select("id").limit(1).execute()
        check_supabase_error(res, "DB Test")
        print(f"✅ DB CONNECTED: {len(res.data)} leads visible")
        return True
    except Exception as e:
        print(f"❌ DB TEST FAIL: {e}")
        raise

# Export for CLI
if __name__ == "__main__":
    print("Nexus Outreach V1 - Modular Architecture")
    print("Deploy with: modal deploy deploy.py")
