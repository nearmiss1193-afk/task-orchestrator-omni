import os
import json
import re
import requests
import traceback
from datetime import datetime, timezone
from core.apps import engine_app as app
from core.constants import SERVICE_KNOWLEDGE, DAN_PHONE, GHL_NOTIFY_WEBHOOK, MAYA_NUMBER, BOOKING_LINK, DAN_EMAILS
from modules.database.supabase_client import get_supabase
from modules.utils.phone import normalize_phone
from modules.voice.sales_persona import get_persona_prompt

# ──────────────────────────────────────────────────────────
#  VAPI WEBHOOK (Voice AI Orchestrator)
# ──────────────────────────────────────────────────────────

@app.function(image=os.environ.get("MODAL_IMAGE_NAME"), secrets=[os.environ.get("MODAL_VAULT_NAME")])
@modal.fastapi_endpoint(method="POST")
def vapi_webhook(data: dict = None):
    """
    Absolute Hardened Vapi Webhook (Modular Port)
    Handles Assistant Requests (Memory/Persona) and Call Completion Reports.
    """
    if data is None: data = {}
    message = data.get("message", {})
    event_type = message.get("type", "unknown")
    call = message.get("call", {})
    
    # Early telemetry exit
    if event_type in ["speech-update", "status-update", "conversation-update", "user-interrupted"]:
        return {"status": "received", "event": event_type}

    try:
        # Context Parsing
        direction = call.get("direction") or call.get("type") or "unknown"
        if "inbound" in direction.lower(): direction = "inbound"
        elif "outbound" in direction.lower(): direction = "outbound"
        
        customer = message.get("customer") or call.get("customer") or {}
        raw_phone = customer.get("number") or call.get("customerNumber") or call.get("to") or ""
        caller_phone = normalize_phone(raw_phone)
        dialed_number = normalize_phone(call.get("to", ""))
        
        is_maya_call = (dialed_number == MAYA_NUMBER or "9362984339" in dialed_number)
        call_mode = "explainer" if is_maya_call else "support"
        summary = message.get("summary") or ""
        transcript = message.get("transcript") or ""

        print(f"📞 [VAPI] {event_type} | Mode: {call_mode} | Phone: {caller_phone}")

        # 1. TOOL CALLS (Maya specific)
        if event_type == "tool-calls":
            tool_calls = message.get("toolCalls", [])
            results = []
            for tc in tool_calls:
                func = tc.get("function", {})
                if func.get("name") == "lookup_business":
                    # This tool implementation would move to a worker/module
                    from workers.audit_generator import lookup_business_google # Assuming this exists or will be ported
                    res_data = lookup_business_google(func.get("arguments", {}).get("business_name"))
                    results.append({"toolCallId": tc.get("id"), "result": json.dumps(res_data)})
            return {"results": results}

        # 2. ASSISTANT REQUEST (Persona + Memory)
        if event_type == "assistant-request":
            customer_name = ""
            context_summary = {}
            lookup_status = "PENDING"
            
            if caller_phone:
                try:
                    supabase = get_supabase()
                    result = supabase.table("customer_memory").select("*").eq("phone_number", caller_phone).limit(1).execute()
                    if result.data:
                        customer_data = result.data[0]
                        context_data = customer_data.get("context_summary", {})
                        context_summary = {"history": context_data} if isinstance(context_data, str) else context_data
                        customer_name = context_summary.get("contact_name") or customer_data.get("customer_name") or ""
                        lookup_status = "FOUND"
                        if context_summary.get("call_purpose") == "sales": call_mode = "sales"
                    else:
                        lookup_status = "NOT_FOUND"
                except Exception as e:
                    print(f"⚠️ [MEMORY] Lookup fail: {e}")
                    lookup_status = "ERROR"

            # Dynamic Greeting & Prompt
            greeting = f"INBOUND CALL - {'RETURNING: ' + customer_name if customer_name else 'NEW Customer'}"
            context_injection = f"\nCUSTOMER CONTEXT: {json.dumps(context_summary)}\n" if context_summary else ""
            
            system_prompt = get_persona_prompt(
                call_mode=call_mode,
                greeting_instruction=greeting,
                context_injection=context_injection,
                service_knowledge=SERVICE_KNOWLEDGE
            )

            assistant_overrides = {
                "variableValues": {"customerPhone": caller_phone, "customerName": customer_name, "callMode": call_mode},
                "systemPrompt": system_prompt
            }
            if is_maya_call:
                assistant_overrides["firstMessage"] = "Thank you for connecting, I'm Maya, I hope you're having a fantastic day! How can I help you today?"

            # Log Debug
            try:
                supabase.table("vapi_debug_logs").insert({
                    "event_type": event_type,
                    "normalized_phone": caller_phone,
                    "lookup_result": lookup_status,
                    "customer_name_found": customer_name,
                    "call_direction": direction,
                    "assistant_overrides_sent": assistant_overrides
                }).execute()
            except: pass

            return {
                "assistant": {
                    "name": "Maya" if is_maya_call else "Sarah",
                    "model": {"provider": "openai", "model": "gpt-4o", "messages": [{"role": "system", "content": system_prompt}]}
                },
                "assistantOverrides": assistant_overrides
            }

        # 3. END OF CALL REPORT (Persistence)
        if event_type == "end-of-call-report":
            if caller_phone:
                try:
                    supabase = get_supabase()
                    
                    # Permanent Transcription Storage (User Requirement: Phase 29)
                    try:
                        supabase.table("call_transcripts").insert({
                            "call_id": call.get("id"),
                            "phone_number": caller_phone,
                            "direction": direction,
                            "summary": summary,
                            "transcript": transcript,
                            "created_at": datetime.now(timezone.utc).isoformat()
                        }).execute()
                    except Exception as trans_err:
                        print(f"⚠️ [TRANSCRIPT] Permanent save failed: {trans_err}")

                    # Name extraction from transcript
                    name_match = re.search(r"(?:name is|i'm|this is|call me)\s+([A-Z][a-z]+)", transcript, re.I)
                    extracted_name = name_match.group(1).title() if name_match else ""
                    
                    # Update Memory
                    res = supabase.table("customer_memory").select("context_summary").eq("phone_number", caller_phone).limit(1).execute()
                    ctx = res.data[0].get("context_summary") or {} if res.data else {}
                    if isinstance(ctx, str): ctx = {"history": ctx}
                    
                    new_hist = f"{ctx.get('history','')}\n[{direction.upper()} {datetime.now(timezone.utc).strftime('%m/%d %H:%M')}]: {summary or 'Call ended'}"
                    ctx["history"] = new_hist[-2000:]
                    if extracted_name: ctx["contact_name"] = extracted_name
                    
                    supabase.table("customer_memory").upsert({"phone_number": caller_phone, "context_summary": ctx}, on_conflict="phone_number").execute()
                    
                    # Notify Dan
                    notify_payload = {
                        "phone": DAN_PHONE,
                        "message": f"📞 Call Summary: {caller_phone}\nName: {extracted_name or 'Unknown'}\nSum: {(summary or 'No summary')[:150]}"
                    }
                    requests.post(GHL_NOTIFY_WEBHOOK, json=notify_payload, timeout=10)
                except Exception as e:
                    print(f"⚠️ [REPORT] Processing fail: {e}")
            
            return {"status": "logged"}

        return {"status": "received"}
    except Exception as e:
        print(f"❌ VAPI WEBHOOK ERROR: {e}")
        traceback.print_exc()
        return {"status": "error_handled", "error": str(e)}

# ──────────────────────────────────────────────────────────
#  GHL WEBHOOK (CRM Sync)
# ──────────────────────────────────────────────────────────

@app.function(image=os.environ.get("MODAL_IMAGE_NAME"), secrets=[os.environ.get("MODAL_VAULT_NAME")])
@modal.fastapi_endpoint(method="POST")
def ghl_webhook(data: dict = None):
    """Consolidated GHL Webhook Listener."""
    from modules.handlers.webhooks import ghl_webhook_logic
    return ghl_webhook_logic(data)

# ──────────────────────────────────────────────────────────
#  SMS INBOUND (Sarah AI)
# ──────────────────────────────────────────────────────────

@app.function(image=os.environ.get("MODAL_IMAGE_NAME"), secrets=[os.environ.get("MODAL_VAULT_NAME")])
@modal.fastapi_endpoint(method="POST")
def sms_inbound(data: dict = None):
    """Modular SMS Inbound Handler with Grok Intelligence."""
    if data is None: data = {}
    from workers.ai_reply import generate_sarah_reply # This worker handles the LLM logic
    
    phone = data.get("phone", "")
    message = data.get("message", "")
    name = data.get("contact_name", "there")
    
    print(f"💬 SMS from {phone}: {message[:50]}...")
    
    try:
        reply = generate_sarah_reply(phone, message, name)
        return {"sarah_reply": reply, "status": "success"}
    except Exception as e:
        print(f"❌ SMS ERROR: {e}")
        return {"sarah_reply": "Hey! I'll have Dan reach out shortly. -Sarah", "status": "fallback"}

# ──────────────────────────────────────────────────────────
#  STRIPE WEBHOOK (Revenue Triage)
# ──────────────────────────────────────────────────────────

@app.function(image=os.environ.get("MODAL_IMAGE_NAME"), secrets=[os.environ.get("MODAL_VAULT_NAME")])
@modal.fastapi_endpoint(method="POST")
def stripe_webhook(data: dict = None):
    """Handles payment mapping and 'customer' status promotion."""
    from modules.handlers.webhooks import stripe_webhook_logic
    # Note: request body would normally be passed as bytes for signature verification, 
    # but for this port we match the existing JSON-based logic.
    return stripe_webhook_logic(json.dumps(data).encode(), "")
