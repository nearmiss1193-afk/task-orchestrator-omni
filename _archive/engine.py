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
from workers.wisdom_engine import daily_wisdom_cron, synthesize_wisdom
from workers.horizon_watcher import run_evolutionary_loop
from workers.sandbox_worker import execute_sandbox_pulse

@app.function(image=image, secrets=[VAULT]) # Schedule disabled to satisfy 5-cron limit
def daily_horizon_scan():
    """Daily autonomous market and capability scan"""
    run_evolutionary_loop()

@app.function(image=image, secrets=[VAULT])
def trigger_vercel_redeploy():
    """Manually trigger a Vercel rebuild via Deploy Hook"""
    import requests
    import os
    hook_url = os.environ.get("VERCEL_DEPLOY_HOOK_URL")
    if not hook_url:
        print("⚠️ VERCEL_DEPLOY_HOOK_URL not set. Skipping redeploy.")
        return False
        
    print(f"🔄 Triggering Vercel Redeploy...")
    res = requests.post(hook_url)
    if res.status_code == 201:
        print("✅ Vercel Redeploy Triggered Successfully.")
        return True
    else:
        print(f"❌ Vercel Redeploy Failed: {res.status_code} - {res.text}")
        return False

@app.function(image=image, secrets=[VAULT])
def sandbox_outreach(lead_id: str):
    """Worker for 1% experimental routing"""
    execute_sandbox_pulse(lead_id)

@app.function(image=image, secrets=[VAULT])
def check_readiness():
    """Verify system state and queue preparedness"""
    from modules.database.supabase_client import get_supabase
    sb = get_supabase()
    
    # 1. Check Campaign Mode
    state = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
    mode = state.data[0]['status'] if state.data else "NOT FOUND"
    print(f"📡 Campaign Mode: {mode}")
    
    # 2. Check Lead Queue
    research_ready = sb.table("contacts_master").select("id", count="exact").eq("status", "new").execute()
    outreach_ready = sb.table("contacts_master").select("id", count="exact").eq("status", "research_done").execute()
    
    print(f"📊 Queue Stats:")
    print(f"   - Needs Research: {research_ready.count}")
    print(f"   - Ready for Outreach: {outreach_ready.count}")
    
    # 3. Last Heartbeat
    hb = sb.table("system_health_log").select("checked_at").order("checked_at", desc=True).limit(1).execute()
    last_hb = hb.data[0]['checked_at'] if hb.data else "NEVER"
    print(f"💓 Last Heartbeat: {last_hb}")
    return True

if __name__ == "__main__":
    print("Nexus Engine - Starting Deployment...")
