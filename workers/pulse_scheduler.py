"""
MISSION: UNIFIED PULSE SCHEDULER
Single orchestrator handling all queue priorities (Grok Recommendation #4)
"""
import sys

if "/root" not in sys.path:
    sys.path.append("/root")

import modal
from core.image_config import image, VAULT
from core.apps import engine_app as app

@app.function(image=image, secrets=[VAULT]) # Schedule disabled (using Phase 5 Heartbeat instead)
def master_pulse():
    """
    UNIFIED ORCHESTRATOR - Handles all scheduling priorities:
    - Research: Every 1 min (60 leads/min)
    - Email: Every 10 min (20 leads/batch)
    - SMS: Every 15 min (timezone-aware)
    - Calls: Every 3 min (1 lead/attempt)
    - Heartbeat: Every 5 min
    """
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import check_supabase_error
    import datetime
    
    supabase = get_supabase()
    now = datetime.datetime.now()
    minute = now.minute
    
    print(f"⚡ MASTER PULSE: Minute {minute}")
    
    # HEARTBEAT (Every 5 min)
    if minute % 5 == 0:
        hb_res = supabase.table("system_health_log").insert({
            "status": "working",
            "check_type": "pulse",
            "checked_at": now.isoformat()
        }).execute()
        check_supabase_error(hb_res, "Heartbeat")
        print("💓 HEARTBEAT LOGGED")
    
    # --- SENTINEL CHECK (Phase 6 Anomaly Guard) ---
    state_res = supabase.table("system_state").select("status").eq("key", "campaign_mode").execute()
    check_supabase_error(state_res, "Check Campaign Mode")
    campaign_mode = state_res.data[0]['status'] if state_res.data else "broken"
    
    if campaign_mode == "broken":
        print("🛑 SENTINEL HALT: Campaign mode is 'broken'. Pulse aborted.")
        return {"status": "halted", "reason": "campaign_mode_broken"}

    def sentinel_guard(supabase):
        """Checks for anomalies and triggers kill-switch if needed"""
        from utils.error_handling import brain_log
        
        # 1. Check last 10 RELEVANT touches for failure rate (ignore live call info)
        touches = supabase.table("outbound_touches")\
            .select("status")\
            .neq("company", "Live Call Info")\
            .order("ts", desc=True)\
            .limit(10)\
            .execute()
        
        if touches.data:
            failures = [t for t in touches.data if t['status'] in ['failed', 'error']]
            if len(failures) >= 5: # 50% failure rate
                print(f"🚨 SENTINEL TRIGGERED: {len(failures)}/10 failures detected!")
                supabase.table("system_state").update({"status": "broken"}).eq("key", "campaign_mode").execute()
                brain_log(supabase, f"SENTINEL TRIGGERED: {len(failures)}/10 failures detected.", "CRITICAL")
                return True
        return False

    if sentinel_guard(supabase):
        return {"status": "halted", "reason": "sentinel_triggered"}
    
    # ---------------------------------------------

    # PRIORITY 1: RESEARCH (Throttled: 10 leads/min to save Supabase writes)
    from workers.research import research_lead_logic
    new_leads_res = supabase.table("contacts_master")\
        .select("id")\
        .eq("status", "new")\
        .not_.is_("website_url", "null")\
        .neq("website_url", "")\
        .limit(10)\
        .execute()
    check_supabase_error(new_leads_res, "Fetch New Leads")
    
    if new_leads_res.data:
        for lead in new_leads_res.data:
            research_lead_logic.spawn(lead['id'])
        print(f"🕵️ RESEARCH: Spawned {len(new_leads_res.data)} tasks (Throttled)")
    
    # PRIORITY 2: EMAIL (Throttled: 5 leads / 10 min)
    if minute % 10 == 0:
        from workers.outreach import dispatch_email_logic
        from workers.sandbox_worker import is_sandbox_lead, execute_sandbox_pulse
        
        email_ready_res = supabase.table("contacts_master")\
            .select("id")\
            .eq("status", "research_done")\
            .limit(5)\
            .execute()
        check_supabase_error(email_ready_res, "Fetch Email Ready")
        
        if email_ready_res.data:
            for lead in email_ready_res.data:
                if is_sandbox_lead(lead['id']):
                    print(f"🧪 [SANDBOX] Routing lead {lead['id']} to experimental path.")
                    execute_sandbox_pulse(lead['id']) # Local spawn or .spawn() if Modal
                else:
                    dispatch_email_logic.spawn(lead['id'])
            print(f"📧 EMAIL: Dispatched {len(email_ready_res.data)} outreach tasks (Throttled)")
    
    # PRIORITY 3: CALLS (Throttled: 1 lead / 3 min, Max 20/day)
    # [Call logic remains mainly standard due to high-friction, but could be sandboxed later]
    if minute % 3 == 0:
        from workers.outreach import dispatch_call_logic
        import pytz
        from utils.error_handling import brain_log
        
        def is_business_hours():
            est = pytz.timezone('US/Eastern')
            now_est = datetime.datetime.now(est)
            if now_est.weekday() >= 6:  # Sunday
                return False
            return 8 <= now_est.hour < 18
        
        if is_business_hours():
            # CHECK DAILY CAP
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            calls_today = supabase.table("outbound_touches")\
                .select("id", count="exact")\
                .eq("channel", "call")\
                .gte("ts", today)\
                .execute()
            
            if calls_today.count >= 20:
                print(f"🛑 CALL CAP REACHED: {calls_today.count} calls today")
                brain_log(supabase, "Vapi Daily Call Cap reached (20)", "WARN")
            else:
                call_ready_res = supabase.table("contacts_master")\
                    .select("id")\
                    .in_("status", ["research_done", "outreach_sent"])\
                    .not_.is_("phone", "null")\
                    .order("last_contacted_at")\
                    .limit(1)\
                    .execute()
                check_supabase_error(call_ready_res, "Fetch Call Target")
                
                if call_ready_res.data:
                    dispatch_call_logic.spawn(call_ready_res.data[0]['id'])
                    print(f"📞 CALL: Spawned dial task ({calls_today.count + 1}/20)")
        else:
            print("⏰ CALL: Outside business hours")
    
    # PRIORITY 4: SMS (Throttled: 5 leads / 15 min)
    if minute % 15 == 0:
        from workers.outreach import dispatch_sms_logic
        from workers.sandbox_worker import is_sandbox_lead, execute_sandbox_pulse
        import pytz
        
        # Simple timezone check
        est = pytz.timezone('US/Eastern')
        now_est = datetime.datetime.now(est)
        hour_est = now_est.hour
        
        if 8 <= hour_est < 18 and now_est.weekday() < 6:
            sms_ready_res = supabase.table("contacts_master")\
                .select("id")\
                .eq("status", "research_done")\
                .not_.is_("phone", "null")\
                .limit(5)\
                .execute()
            check_supabase_error(sms_ready_res, "Fetch SMS Ready")
            
            if sms_ready_res.data:
                for lead in sms_ready_res.data:
                    if is_sandbox_lead(lead['id']):
                        print(f"🧪 [SANDBOX] Routing lead {lead['id']} to experimental path.")
                        execute_sandbox_pulse(lead['id'])
                    else:
                        dispatch_sms_logic.spawn(lead['id'])
                print(f"📱 SMS: Dispatched {len(sms_ready_res.data)} outreach tasks (Throttled)")
        else:
            print("⏰ SMS: Outside business hours")
    
    print("✅ PULSE COMPLETE")
