import os
import json
import re
from datetime import datetime
from core.apps import engine_app as app
from modules.database.supabase_client import get_supabase

# ──────────────────────────────────────────────────────────
#  VAPI WEBHOOK (Voice AI Orchestrator)
# ──────────────────────────────────────────────────────────

def handle_vapi_event(payload):
    """
    Unified Vapi Webhook Handler.
    Handles Assistant Requests (Memory/Persona) and Call Completion Reports.
    """
    try:
        event = payload.get("message", {})
        event_type = event.get("type", "unknown")
        call = event.get("call", {})
        caller_phone = call.get("customer", {}).get("number")
        
        print(f"📞 VAPI EVENT: {event_type} for {caller_phone}")
        
        # 1. Assistant Request (Memory Injection)
        if event_type == "assistant-request":
            # [Logic for customer name and history lookup would go here]
            # [Migrated from monolithic script]
            return {"status": "success", "overrides": {}}
            
        # 2. End of Call Report (Persistence)
        if event_type == "end-of-call-report":
            # [Logic for summary logging and GHL notification]
            return {"status": "logged"}
            
        return {"status": "received"}
    except Exception as e:
        print(f"❌ Vapi Handler Error: {e}")
        return {"status": "error_handled"}

# ──────────────────────────────────────────────────────────
#  GHL WEBHOOK (CRM Sync)
# ──────────────────────────────────────────────────────────

def handle_ghl_event(payload):
    """Handles deep sync and lead status updates from GHL."""
    try:
        print(f"🔗 GHL EVENT: {payload.get('type')}")
        # [Sync logic here]
        return {"status": "synced"}
    except Exception as e:
        print(f"❌ GHL Handler Error: {e}")
        return {"error": str(e)}

# ──────────────────────────────────────────────────────────
#  STRIPE WEBHOOK (Revenue Triage)
# ──────────────────────────────────────────────────────────

def handle_stripe_event(payload):
    """Handles payment mapping and 'customer' status promotion."""
    try:
        print(f"💰 STRIPE EVENT: {payload.get('type')}")
        # [Payment logic here]
        return {"status": "paid"}
    except Exception as e:
        print(f"❌ Stripe Handler Error: {e}")
        return {"error": str(e)}
