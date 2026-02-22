import os
import json
import requests
from datetime import datetime
from core.constants import SERVICE_KNOWLEDGE, GHL_NOTIFY_WEBHOOK, DAN_PHONE, BOOKING_LINK
from modules.database.supabase_client import get_supabase

def handle_inbound_email(sender_email: str, subject: str, text_body: str):
    """
    Parses inbound emails, records them in customer memory, and auto-replies if intent matches.
    """
    if not os.environ.get("GROK_API_KEY"):
        from dotenv import load_dotenv
        load_dotenv()
        
    supabase = get_supabase()
    customer_id = None
    contact_name = "there"
    
    # --- FIND LEAD RECORD ---
    try:
        lead_match = supabase.table("contacts_master").select("*").eq("email", sender_email).limit(1).execute()
        if lead_match.data:
            lead = lead_match.data[0]
            contact_name = lead.get("first_name") or lead.get("company_name") or "there"
            customer_id = lead.get("id")
            
            # Record touch
            supabase.table("outbound_touches").insert({
                "lead_id": customer_id,
                "company_name": lead.get("company_name", "Unknown"),
                "channel": "email",
                "campaign_id": "inbound_triage",
                "status": "received",
                "replied": True,
                "ts": datetime.utcnow().isoformat()
            }).execute()
    except Exception as e:
        print(f"⚠️ Failed to look up email sender {sender_email}: {e}")
        
    # --- AI TRIAGE (Grok) ---
    SARAH_EMAIL_PROMPT = f"""You are Sarah, AI executive assistant for AI Service Co.
    
    MISSION: Read this inbound client email and determine if they want to book a call/demo.
    
    CONVERSATION RULES:
    - If they are asking for a meeting, call, demo, or next steps -> intent is "booking".
    - If they are asking a technical question -> intent is "support".
    - If they are saying not interested or unsubscribe -> intent is "opt_out".
    - Otherwise -> intent is "general".
    
    {SERVICE_KNOWLEDGE}
    
    OUTPUT FORMAT:
    You must respond in valid JSON format ONLY with two keys:
    {{"reply": "A brief, professional 1-2 sentence reply as Sarah. Keep it very conversational.", "intent": "booking" | "support" | "opt_out" | "general"}}
    """

    api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
    if not api_key:
        print("⚠️ No GROK API key found for email triage.")
        return {"status": "error", "message": "No API key"}
        
    reply = "Thank you for getting back to us. I have forwarded your message to Dan."
    intent = "general"
    
    try:
        messages = [
            {"role": "system", "content": SARAH_EMAIL_PROMPT},
            {"role": "user", "content": f"Incoming Email from {sender_email} ({contact_name})\nSubject: {subject}\n\n{text_body}"}
        ]
        
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "messages": messages,
                "model": "grok-3",
                "temperature": 0.5,
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content'].strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            
            try:
                parsed = json.loads(content)
                reply = parsed.get("reply", reply)
                intent = parsed.get("intent", "general")
            except Exception as e:
                print(f"⚠️ JSON Parse error on email triage: {e}")
    except Exception as e:
        print(f"⚠️ Grok API Error on email triage: {e}")
        
    # --- ACTION ROUTING ---
    final_reply_html = f"<p>{reply}</p>"
    
    if intent == "booking":
        final_reply_html += f'<br><p><a href="{BOOKING_LINK}" style="display:inline-block; background:#2563eb; color:#fff; padding:12px 24px; border-radius:6px; text-decoration:none; font-weight:bold;">Book a 15-min call with Dan</a></p>'
    elif intent == "opt_out" and customer_id:
        # Mark as DNC in DB
        supabase.table("contacts_master").update({"status": "no_contact_info"}).eq("id", customer_id).execute()
        final_reply_html = "" # We don't reply to opt-outs

    # --- DISPATCH EMAIL AUTO-REPLY VIA RESEND ---
    if final_reply_html:
        resend_key = os.environ.get("RESEND_API_KEY")
        if resend_key:
            resend_url = "https://api.resend.com/emails"
            payload = {
                "from": "Sarah <owner@aiserviceco.com>",
                "to": [sender_email],
                "subject": f"Re: {subject}",
                "html": final_reply_html + "<br><br><small>Sarah<br>AI Executive Assistant<br>AI Service Co.</small>"
            }
            try:
                res = requests.post(
                    resend_url,
                    headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                    json=payload
                )
                print(f"📧 Sent auto-reply to {sender_email}. Status: {res.status_code}")
            except Exception as e:
                print(f"⚠️ Failed to send Resend auto-reply: {e}")

    # --- NOTIFY DAN ---
    try:
        alert_msg = f"📧 INBOUND EMAIL\nFrom: {sender_email}\nSubj: {subject}\nIntent: {intent.upper()}\n\nSarah replied: {reply}"
        requests.post(GHL_NOTIFY_WEBHOOK, json={"phone": DAN_PHONE, "message": alert_msg}, timeout=5)
    except: pass
    
    return {"status": "processed", "intent": intent, "reply": reply}
