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
    Includes EMPIRE: Command Relay for remote SMS authority.
    """
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import brain_log
    import os

    try:
        msg_body = data.get('message', {}).get('body', '')
        msg_type = data.get('type')
        contact_id = data.get('contact_id')
        
        print(f"📥 GHL WEBHOOK: {msg_type} from {contact_id}")

        # SOVEREIGN COMMAND BRIDGE: Listen for EMPIRE: prefix (DORMANT - BOARD REQUEST)
        # if msg_body.upper().startswith("EMPIRE:"):
        #     print(f"⚠️ COMMAND DETECTED: {msg_body}")
        #     parts = msg_body.split()
        #     # Format: EMPIRE: [PASSCODE] [COMMAND] [ARGS...]
        #     if len(parts) >= 3 and parts[1] == "1117":
        #         command = parts[2].upper()
        #         args = parts[3:]
        #         sb = get_supabase()
        #         brain_log(sb, f"SOVEREIGN COMMAND: {command} with args {args}", "WARNING")
        #         if command == "STRIKE":
        #             from workers.outreach import sync_ghl_contacts
        #             limit = int(args[0]) if args else 10
        #             print(f"🚀 COMMAND: Executing STRIKE batch of {limit}")
        #             sync_ghl_contacts.spawn()
        #         return {"status": "command_executed", "command": command}
        #     else:
        #         print("❌ COMMAND FAILED: Invalid passcode or format")
        #         return {"status": "command_failed", "reason": "auth_failure"}

        return {"status": "received"}
    except Exception as e:
        print(f"❌ GHL WEBHOOK ERROR: {e}")
        return {"status": "error"}

async def vercel_webhook(data: dict):
    """
    Handle Vercel deployment notifications.
    """
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import brain_log
    
    try:
        type = data.get('type')
        payload = data.get('payload', {})
        deployment = payload.get('deployment', {})
        url = deployment.get('url') or "N/A"
        project = payload.get('project', {}).get('name') or "Empire-Unified"
        
        print(f"🚀 VERCEL DEPLOY: {type} | {project} | {url}")
        
        # Log to operational memory (brain_logs)
        sb = get_supabase()
        brain_log(sb, f"VERCEL DEPLOYMENT: {type} for {project}. Live at: {url}", "INFO")
        
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ VERCEL WEBHOOK ERROR: {e}")
        return {"status": "error", "message": str(e)}

async def vanguard_signup(data: dict):
    """
    Handle Vanguard Waitlist signups.
    """
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import check_supabase_error
    
    try:
        email = data.get('email')
        company = data.get('company', 'Unknown')
        
        print(f"🎖️ VANGUARD SIGNUP: {email} from {company}")
        
        supabase = get_supabase()
        
        # Insert or update
        res = supabase.table("contacts_master").upsert({
            "email": email,
            "full_name": f"Vanguard Lead: {company}",
            "ghl_contact_id": f"VANGUARD_{email.split('@')[0]}",
            "status": "interested",
            "lead_source": "vanguard-waitlist",
            "company_name": company
        }, on_conflict="email").execute()
        check_supabase_error(res, "Vanguard Signup")
        
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ VANGUARD SIGNUP ERROR: {e}")
        return {"status": "error", "message": str(e)}

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

    # 6. SENTINEL METRICS (Phase 6)
    sentinel_score = 100
    try:
        if comms.data:
            failures = [t for t in comms.data if t['status'] == 'failed']
            sentinel_score = 100 - (len(failures) * 10)
    except Exception:
        pass

    # 7. HORIZON INSIGHTS (Phase 7)
    horizon_insights = []
    try:
        # Fetch latest Phase 7 insights
        h_res = sb.table("system_wisdom")\
            .select("topic, insight, examples")\
            .eq("category", "horizon_rd")\
            .order("created_at", desc=True)\
            .limit(3)\
            .execute()
        if h_res.data:
            for h in h_res.data:
                # Map to a flat structure for the dashboard UI
                horizon_insights.append({
                    "topic": h['topic'],
                    "insight": h['insight'],
                    "strategy": h.get('examples', {}).get('opportunity') or "Evolutionary Path"
                })
    except Exception:
        pass

    return {
        "health": sentinel_score if mode == "working" else 20,
        "mode": mode,
        "funnel": status_counts,
        "recent_comms": comms.data,
        "total_leads": sum(status_counts.values()),
        "wisdom_score": wisdom_count,
        "pipeline_value": pipeline_value,
        "outreach_burn": round(outreach_burn, 2),
        "sentinel_score": sentinel_score,
        "horizon_insights": horizon_insights
    }
