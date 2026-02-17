import os
import json
import requests
from datetime import datetime, timezone, timedelta
from modules.database.supabase_client import get_supabase

def run_system_heartbeat(issues):
    """Health check + heartbeat logger."""
    print(f"HEARTBEAT: Running at {datetime.now(timezone.utc).isoformat()}")
    try:
        supabase = get_supabase()
        
        # 1. Check Campaign Mode
        campaign = supabase.table("system_state").select("status").eq("key", "campaign_mode").execute()
        mode = campaign.data[0].get("status") if campaign.data else "unknown"
        if mode != "working":
            issues.append(f"Campaign mode is '{mode}'")
            
        # 2. Log Pulse
        supabase.table("system_health_log").insert({
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "check_type": "heartbeat_v3_modular",
            "status": "ok" if not issues else "degraded",
            "details": {"issues": issues}
        }).execute()
        return mode
    except Exception as e:
        print(f"Heartbeat Error: {e}")
        return "error"

def run_self_healing():
    """Independent self-healing and staleness checks."""
    issues = []
    try:
        supabase = get_supabase()
        
        # 1. Outreach Stall Check
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
        recent = supabase.table("outbound_touches").select("id", count="exact").gte("ts", cutoff).execute()
        count = recent.count if recent.count is not None else 0
        if count == 0: issues.append("OUTREACH STALLED")
        
        # 2. Lead Pool Check
        pool = supabase.table("contacts_master").select("id", count="exact").in_("status", ["new", "research_done"]).execute()
        if (pool.count or 0) == 0: issues.append("LEAD POOL EMPTY")
        
    except Exception as e:
        print(f"Self-Healing Error: {e}")
    return issues

def trigger_enrichment_worker(lead_id):
    """Asynchronous trigger for research strike."""
    # This will be imported and called via .spawn from the switchboard
    pass
