"""
NEXUS ENGINE - SOVEREIGN OUTREACH CORE
Dedicated entry point for background workers and crons.
"""
import sys
if "/root" not in sys.path:
    sys.path.append("/root")

# Import core infrastructure
from core.image_config import image, VAULT
from core.apps import engine_app as app

# Import workers (this registers them with the app)
from workers.research import research_lead_logic
from workers.outreach import dispatch_email_logic, dispatch_sms_logic, dispatch_call_logic
from workers.pulse_scheduler import master_pulse

@app.function(image=image, secrets=[VAULT])
def test_engine_connectivity():
    """Quick DB connectivity test for the engine"""
    from modules.database.supabase_client import get_supabase
    sb = get_supabase()
    res = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
    print(f"✅ ENGINE ONLINE. Campaign Mode: {res.data[0]['status'] if res.data else 'Unknown'}")
    return True

if __name__ == "__main__":
    print("Nexus Engine - Starting Deployment...")
