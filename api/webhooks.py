"""
MISSION: API & WEBHOOK HANDLERS
Consolidated webhook endpoints for Vapi, GHL, and Dashboard
"""
import sys
if "/root" not in sys.path:
    sys.path.append("/root")

from fastapi import Request
import modal
from core.image_config import image, portal_image, VAULT
from core.apps import portal_app as app

async def vapi_webhook(data: dict):
    """
    Handle Vapi call status updates and transcriptions.
    """
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import check_supabase_error
    
    try:
        call_id = data.get('message', {}).get('call', {}).get('id')
        if not call_id:
            return {"status": "ignored", "reason": "no_call_id"}
            
        print(f"📞 VAPI WEBHOOK: {data.get('message', {}).get('type')} for {call_id}")
        
        # Log to DB (Rule #1 - Database Results)
        supabase = get_supabase()
        touch_res = supabase.table("outbound_touches").insert({
            "phone": data.get('message', {}).get('call', {}).get('customer', {}).get('number'),
            "channel": "call",
            "company": "Live Call Info",
            "status": data.get('message', {}).get('type'),
            "payload": data.get('message', {}),
            "meta": {"call_id": call_id}
        }).execute()
        check_supabase_error(touch_res, "Vapi Webhook Log")
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ VAPI WEBHOOK ERROR: {e}")
        return {"status": "error", "message": str(e)}

async def ghl_webhook(data: dict):
    """
    Handle incoming GHL webhooks.
    """
    try:
        print(f"📥 GHL WEBHOOK: {data.get('type')}")
        return {"status": "received"}
    except Exception as e:
        print(f"❌ GHL WEBHOOK ERROR: {e}")
        return {"status": "error"}

async def vercel_webhook(data: dict):
    """
    Handle Vercel deployment notifications.
    """
    try:
        print(f"🚀 VERCEL WEBHOOK: {data.get('type')} - {data.get('payload', {}).get('deployment', {}).get('url')}")
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ VERCEL WEBHOOK ERROR: {e}")
        return {"status": "error"}

def dashboard_stats():
    """
    Consolidated dashboard stats for the Sovereign Command.
    """
    from modules.database.supabase_client import get_supabase
    sb = get_supabase()
    
    # 1. FUNNEL STATS
    status_counts = {}
    statuses = ["new", "researching", "research_done", "outreach_dispatched", "dnd_blocked", "replied", "calling_initiated", "interested"]
    for s in statuses:
        res = sb.table("contacts_master").select("id", count="exact").eq("status", s).execute()
        status_counts[s] = res.count or 0
        
    # 2. RECENT COMMS
    comms = sb.table("outbound_touches")\
        .select("channel, status, company, ts")\
        .order("ts", desc=True)\
        .limit(10)\
        .execute()
        
    # 3. SYSTEM STATE
    state = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
    mode = state.data[0]['status'] if state.data else "unknown"
    
    # 4. WISDOM CACHE
    wisdom_count = 0
    try:
        wisdom_res = sb.table("system_wisdom").select("id", count="exact").execute()
        wisdom_count = wisdom_res.count or 0
    except Exception:
        pass

    # 5. ROI & FINANCIALS (Phase 4)
    pipeline_value = 0
    outreach_burn = 0
    try:
        # Sum potential revenue (ignoring skipped/dnd)
        rev_res = sb.table("contacts_master").select("deal_value").not_.in_("status", ["skipped_no_url", "dnd_blocked"]).execute()
        if rev_res.data:
            pipeline_value = sum([float(r.get('deal_value') or 497) for r in rev_res.data])
        
        # Estimate Burn (Rule of thumb: 0.15 per call, 0.01 per email/sms)
        touches = sb.table("outbound_touches").select("channel").execute()
        if touches.data:
            for t in touches.data:
                if t['channel'] == 'call': outreach_burn += 0.15
                else: outreach_burn += 0.01
    except Exception as e:
        print(f"⚠️ ROI Calc Error: {e}")

    return {
        "health": 95 if mode == "working" else 20,
        "mode": mode,
        "funnel": status_counts,
        "recent_comms": comms.data,
        "total_leads": sum(status_counts.values()),
        "wisdom_score": wisdom_count,
        "pipeline_value": pipeline_value,
        "outreach_burn": round(outreach_burn, 2)
    }
