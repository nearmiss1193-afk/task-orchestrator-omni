"""
MISSION: VAPI METADATA INJECTOR (Phase 5)
Bypassing real-time bridge latencies by injecting lead context 
directly into the Vapi outbound call payload.
"""

import os
import sys

def generate_vapi_metadata(phone_number, supabase):
    """
    Fetches lead context from Supabase and builds a metadata dictionary for Vapi.
    """
    print(f"🧠 METADATA: Generating context for {phone_number}...")
    
    metadata = {
        "customer_phone": phone_number,
        "system_version": "v5.0-sovereign",
        "timestamp": "2026-02-09"
    }

    try:
        # 1. Lookup in contacts_master
        lead_res = supabase.table("contacts_master").select("*").eq("phone", phone_number).limit(1).execute()
        if lead_res.data:
            lead = lead_res.data[0]
            metadata["customer_name"] = lead.get("full_name", "there")
            metadata["company_name"] = lead.get("company_name", "Unknown")
            metadata["industry"] = lead.get("industry", "Business")
            
            # 2. Lookup in customer_memory for interaction history
            mem_res = supabase.table("customer_memory").select("context_summary").eq("phone_number", phone_number).limit(1).execute()
            if mem_res.data:
                metadata["last_context"] = mem_res.data[0].get("context_summary", {}).get("history", "")[:500]
            
            # 3. Lookup in master_lead_dossier for pipeline status
            dossier_res = supabase.table("master_lead_dossier").select("*").eq("contact_id", lead['id']).limit(1).execute()
            if dossier_res.data:
                dossier = dossier_res.data[0]
                metadata["ghl_status"] = dossier.get("ghl_status", "unknown")
                metadata["email_engagement"] = "high" if dossier.get("email_open_count", 0) > 0 else "low"

        else:
            print(f"⚠️ METADATA: Lead {phone_number} not found in contacts_master.")
            metadata["customer_name"] = "there"

    except Exception as e:
        print(f"❌ METADATA Error: {e}")
        metadata["error"] = str(e)

    return metadata

def inject_metadata_into_payload(payload, metadata):
    """
    Appends metadata to the Vapi request payload.
    Vapi uses 'customer' or 'metadata' fields depending on the endpoint.
    """
    # Outbound call endpoint uses 'assistantOverrides' to inject system prompt context
    # but we can also use 'customer' for variable injection.
    
    if "assistantOverrides" not in payload:
        payload["assistantOverrides"] = {}
        
    if "variableValues" not in payload["assistantOverrides"]:
        payload["assistantOverrides"]["variableValues"] = {}
        
    # Inject variables that Sarah's prompt uses
    payload["assistantOverrides"]["variableValues"].update(metadata)
    
    # Also attach to top-level metadata for logging
    payload["metadata"] = metadata
    
    return payload
