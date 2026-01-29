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

@app.function(schedule=modal.Cron("*/1 * * * *"), image=image, secrets=[VAULT])
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
        email_ready_res = supabase.table("contacts_master")\
            .select("id")\
            .eq("status", "research_done")\
            .limit(5)\
            .execute()
        check_supabase_error(email_ready_res, "Fetch Email Ready")
        
        if email_ready_res.data:
            ids = [lead['id'] for lead in email_ready_res.data]
            list(dispatch_email_logic.map(ids))
            print(f"📧 EMAIL: Dispatched {len(ids)} emails (Throttled)")
    
    # PRIORITY 3: CALLS (Throttled: 1 lead / 3 min, Max 20/day)
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
                ids = [lead['id'] for lead in sms_ready_res.data]
                list(dispatch_sms_logic.map(ids))
                print(f"📱 SMS: Dispatched {len(ids)} messages (Throttled)")
        else:
            print("⏰ SMS: Outside business hours")

    
    print("✅ PULSE COMPLETE")

