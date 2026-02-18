import os
import json
import requests
import re
from datetime import datetime
from core.constants import SERVICE_KNOWLEDGE, DAN_PHONE, GHL_NOTIFY_WEBHOOK
from modules.database.supabase_client import get_supabase
from modules.utils.phone import normalize_phone

def generate_sarah_reply(phone: str, message: str, contact_name: str = "there"):
    """
    Receives inbound SMS, generates Sarah AI reply with persistent memory.
    """
    phone = normalize_phone(phone)
    supabase = get_supabase()
    
    # --- MEMORY LOOKUP ---
    context_summary = {}
    customer_id = None
    
    try:
        # Lookup by NORMALIZED phone number (E.164 format)
        result = supabase.table("customer_memory").select("*").eq("phone_number", phone).execute()
        
        if result.data:
            customer = result.data[0]
            customer_id = customer["customer_id"]
            context_summary = customer.get("context_summary", {}) or {}
        else:
            # New customer - create record
            new_customer = supabase.table("customer_memory").insert({
                "phone_number": phone,
                "context_summary": {
                    "contact_name": contact_name,
                    "history": f"[System]: Customer {contact_name} started conversation via SMS"
                },
                "status": "active"
            }).execute()
            if new_customer.data:
                customer_id = new_customer.data[0]["customer_id"]
        
        # --- RESEARCH LOOKUP ---
        research_context = ""
        try:
            lead_match = supabase.table("contacts_master").select("raw_research, website_url, company_name").eq("phone", phone).limit(1).execute()
            if lead_match.data:
                lead = lead_match.data[0]
                raw = json.loads(lead.get("raw_research") or "{}")
                ps_score = raw.get("pagespeed", {}).get("score", "N/A")
                privacy = raw.get("privacy", {}).get("status", "unknown")
                
                research_context = f"\nWEBSITE AUDIT FINDINGS: Speed {ps_score}/100, Privacy: {privacy}"
                if privacy == "critical":
                    research_context += "\n- CRITICAL: Missing Privacy Policy (Florida Digital Bill of Rights risk)."
        except: pass
    except Exception as e:
        print(f"⚠️ Memory lookup failed: {e}")
    
    # --- PROMPT CONSTRUCTION ---
    SARAH_PROMPT = f"""You are Sarah, AI assistant for AI Service Co.
    
    MISSION: Identify high-intent leads and pivot immediately to a call with Dan.
    
    CONVERSATION RULES:
    - Keep responses VERY SHORT (1-2 sentences).
    - Be warm but PROFESSIONAL and URGENT.
    - Reference website findings naturally if present.
    - Pivot to a call after 2-3 messages.
    
    {SERVICE_KNOWLEDGE}
    
    {research_context}
    """
    
    # --- LLM CALL (Grok) ---
    api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
    if not api_key:
        return "Hey! I'll have Dan reach out shortly. -Sarah"
    
    try:
        messages = [
            {"role": "system", "content": SARAH_PROMPT},
            {"role": "user", "content": f"Incoming SMS from {contact_name}: \"{message}\". Reply as Sarah:"}
        ]
        
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "messages": messages,
                "model": "grok-3",
                "temperature": 0.7,
                "max_tokens": 100
            },
            timeout=30
        )
        reply = resp.json()['choices'][0]['message']['content'].strip() if resp.status_code == 200 else "Hey! Dan will follow up soon."
    except:
        reply = "Hey! Let me have Dan follow up with you. -Sarah"
    
    # --- LOGGING & NOTIFICATION ---
    try:
        if customer_id:
            supabase.table("conversation_logs").insert({
                "customer_id": customer_id,
                "channel": "sms",
                "direction": "inbound",
                "content": message,
                "sarah_response": reply
            }).execute()
        
        # Notify Dan
        requests.post(GHL_NOTIFY_WEBHOOK, json={
            "phone": DAN_PHONE,
            "message": f"💬 SMS to Sarah\nFrom: {contact_name} ({phone})\nMsg: {message}\nSarah: {reply}"
        }, timeout=5)
    except: pass
    
    return reply
