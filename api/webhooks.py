"""
MISSION: API & WEBHOOK HANDLERS
Consolidated webhook endpoints for Vapi, GHL, and Dashboard
"""
import sys
if "/root" not in sys.path:
    sys.path.append("/root")

from fastapi import Request
import modal
from core.image_config import image, VAULT, app

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
async def vapi_webhook(request: Request):
    """
    Handle Vapi call status updates and transcriptions.
    """
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import check_supabase_error
    import json
    
    try:
        data = await request.json()
        call_id = data.get('message', {}).get('call', {}).get('id')
        if not call_id:
            return {"status": "ignored", "reason": "no_call_id"}
            
        print(f"📞 VAPI WEBHOOK: {data.get('message', {}).get('type')} for {call_id}")
        
        # Log to DB (simplified for MVP)
        supabase = get_supabase()
        # In a real scenario, we'd parse the transcript and update the lead
        # For now, just acknowledged
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ VAPI WEBHOOK ERROR: {e}")
        return {"status": "error", "message": str(e)}

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
async def ghl_webhook(request: Request):
    """
    Handle incoming GHL webhooks (e.g. form submissions, tag updates).
    """
    try:
        data = await request.json()
        print(f"📥 GHL WEBHOOK: {data.get('type')}")
        # Logic to be implemented or ported from legacy if needed
        return {"status": "received"}
    except Exception as e:
        print(f"❌ GHL WEBHOOK ERROR: {e}")
        return {"status": "error"}

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="GET")
def dashboard_stats():
    """
    Public dashboard stats (secured by simple logic if needed)
    """
    from modules.database.supabase_client import get_supabase
    sb = get_supabase()
    
    stats = {}
    
    # Simple counts
    for status in ["new", "research_done", "outreach_sent", "calling_initiated"]:
        res = sb.table("contacts_master").select("id", count="exact").eq("status", status).execute()
        stats[status] = res.count
        
    return stats
