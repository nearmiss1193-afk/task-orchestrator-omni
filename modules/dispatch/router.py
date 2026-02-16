"""
AI DISPATCH ROUTER v1
=====================
Logic for routing leads based on their 'niche' and 'source'.
Handles trade-specific GHL sub-accounts and Maya/Sarah personas.
"""
import json
import os
from modules.database.supabase_client import get_supabase

# Niche Mapping to GHL Location IDs or Specialized Personas
# uFYcZA7Zk6EcBze5B4oH is the baseline Lakeland HVAC account.
DISPATCH_MAP = {
    "hvac": {
        "location_id": "uFYcZA7Zk6EcBze5B4oH",
        "persona": "sarah_hvac",
        "priority": "high",
        "tag": "HVAC_LEAD"
    },
    "plumbing": {
        "location_id": "M7YwDClf34RsNhPQfhS7", # Example secondary ID
        "persona": "sarah_plumbing",
        "priority": "medium",
        "tag": "PLUMBING_LEAD"
    },
    "electrical": {
        "location_id": "uFYcZA7Zk6EcBze5B4oH",
        "persona": "sarah_electrical",
        "priority": "medium",
        "tag": "ELECTRICAL_LEAD"
    },
    "manus": {
        "location_id": "uFYcZA7Zk6EcBze5B4oH",
        "persona": "maya_screener",
        "priority": "critical",
        "tag": "RECRUITMENT_STRIKE"
    },
    "sunbiz": {
        "location_id": "uFYcZA7Zk6EcBze5B4oH",
        "persona": "sarah_hvac", # Default for new registrations
        "priority": "high",
        "tag": "SUNBIZ_DELTA"
    }
}

def route_lead(lead_id: str):
    """
    Analyzes lead data and updates routing-specific metadata.
    """
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase connection failed in router")
        return None
        
    res = supabase.table("contacts_master").select("*").eq("id", lead_id).execute()
    if not res.data:
        print(f"❌ Lead {lead_id} not found for routing")
        return None
        
    lead = res.data[0]
    niche = (lead.get("niche") or "").lower()
    source = (lead.get("source") or "").lower()
    
    # Logic chain: Source (Manus) > Specific Niche > Default (HVAC)
    config = DISPATCH_MAP.get(source) or DISPATCH_MAP.get(niche) or DISPATCH_MAP.get("hvac")
    
    # Update lead status and assigned persona
    update_data = {
        "assigned_to": config["persona"],
        "raw_research": json.dumps({
            **json.loads(lead.get("raw_research") or "{}"),
            "dispatch_config": config,
            "routed_at": datetime.now(timezone.utc).isoformat()
        })
    }
    
    try:
        from datetime import datetime, timezone
        supabase.table("contacts_master").update(update_data).eq("id", lead_id).execute()
        print(f"🚦 lead {lead_id} ({company}) routed to {config['persona']}")
    except Exception as e:
        print(f"⚠️ Failed to update routing for {lead_id}: {e}")
        
    return config

if __name__ == "__main__":
    # Test with a mock run if needed
    pass
