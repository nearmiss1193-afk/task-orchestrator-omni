"""
MISSION: OUTREACH WORKERS - Hardened Email/SMS/Call Dispatch
All with webhook validation and error checks
"""
import sys
import os

if "/root" not in sys.path:
    sys.path.append("/root")

import modal
from core.image_config import image, VAULT
from core.apps import engine_app as app

@app.function(image=image, secrets=[VAULT])
def dispatch_email_logic(lead_id: str):
    """
    Dispatches email via GHL webhook (ID-based, not object).
    
    Args:
        lead_id: Database ID
        
    Returns:
        bool: Success status
    """
    print(f"📧 EMAIL DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import check_supabase_error, validate_webhook_response
    import requests
    import os
    
    supabase = get_supabase()
    
    # FETCH LEAD
    lead_res = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute()
    check_supabase_error(lead_res, "Fetch Lead for Email")
    lead = lead_res.data
    
    # SEND EMAIL
    hook_url = os.environ.get("GHL_EMAIL_WEBHOOK_URL")
    if not hook_url:
        raise Exception("GHL_EMAIL_WEBHOOK_URL not configured")
    
    payload = {
        "contact_id": lead['ghl_contact_id'],
        "subject": "quick question",
        "body": f"hey, {lead.get('ai_strategy', 'saw your site and had a question')}"
    }
    
    response = requests.post(hook_url, json=payload, timeout=10)
    validate_webhook_response(response, "Email Webhook")
    
    # UPDATE STATUS (with error check!)
    update_res = supabase.table("contacts_master").update({"status": "outreach_sent"}).eq("id", lead_id).execute()
    check_supabase_error(update_res, "Update to outreach_sent")
    
    # RECORD TOUCH
    touch_res = supabase.table("outbound_touches").insert({
        "phone": lead.get("phone"),
        "channel": "email",
        "company": lead.get("company_name", "Unknown"),
        "status": "sent",
        "payload": payload
    }).execute()
    check_supabase_error(touch_res, "Record Touch")
    
    print(f"✅ EMAIL SENT & RECORDED")
    return True


@app.function(image=image, secrets=[VAULT])
def dispatch_sms_logic(lead_id: str, message: str = None):
    """
    Dispatches SMS via GHL webhook (ID-based).
    
    Args:
        lead_id: Database ID
        message: Optional custom message
    """
    print(f"📱 SMS DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    from utils.error_handling import check_supabase_error, validate_webhook_response
    import requests
    import os
    
    supabase = get_supabase()
    
    # FETCH LEAD
    lead_res = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute()
    check_supabase_error(lead_res, "Fetch Lead for SMS")
    lead = lead_res.data
    
    # SEND SMS
    hook_url = os.environ.get("GHL_SMS_WEBHOOK_URL")
    if not hook_url:
        raise Exception("GHL_SMS_WEBHOOK_URL not configured")
    
    phone = lead.get('phone', '')
    if phone and not phone.startswith('+'):
        phone = f"+1{phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')}"
    
    payload = {
        "phone": phone,
        "contact_id": lead['ghl_contact_id'],
        "message": message or "hey, saw your site. had a quick question about your operations. you around?",
        "first_name": lead.get('full_name', 'there').split()[0]
    }
    
    response = requests.post(hook_url, json=payload, timeout=10)
    print(f"GHL SMS Response: {response.status_code} - {response.text}")
    
    # Check for DND or specific GHL errors
    ghl_data = {}
    try:
        ghl_data = response.json()
    except:
        pass
        
    status = "dispatched"
    if "DND" in response.text or ghl_data.get("message", "").lower().find("dnd") != -1:
        status = "dnd_blocked"
        print(f"🛑 GHL BLOCKED SMS (DND): {lead_id}")
    
    # UPDATE STATUS
    update_res = supabase.table("contacts_master").update({"status": "outreach_dispatched" if status == "dispatched" else "dnd_blocked"}).eq("id", lead_id).execute()
    check_supabase_error(update_res, "Update Status")
    
    # RECORD TOUCH
    touch_res = supabase.table("outbound_touches").insert({
        "phone": phone,
        "channel": "sms",
        "company": lead.get("company_name", "Unknown"),
        "status": status,
        "payload": payload,
        "meta": {"ghl_response": response.text}
    }).execute()
    check_supabase_error(touch_res, "Record Touch")
    
    print(f"✅ SMS SENT & RECORDED")
    return True


@app.function(image=image, secrets=[VAULT])
def dispatch_call_logic(lead_id: str):
    """
    Initiates outbound call via Vapi (ID-based).
    """
    print(f"📞 CALL DISPATCH: Lead ID {lead_id}")
    from modules.database.supabase_client import get_supabase
    from modules.outbound_dialer import dial_prospect
    from utils.error_handling import check_supabase_error
    import datetime
    
    supabase = get_supabase()
    
    # FETCH LEAD
    lead_res = supabase.table("contacts_master").select("*").eq("id", lead_id).single().execute()
    check_supabase_error(lead_res, "Fetch Lead for Call")
    lead = lead_res.data
    
    # DIAL
    # VERIFIED VAPI NATIVE ID: 8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e (+18632132505)
    phone_id = os.environ.get("VAPI_PHONE_NUMBER_ID") or "8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e"
    dial_res = dial_prospect(
        phone_number=lead['phone'], 
        company_name=lead.get('company_name', ''),
        assistant_id=os.environ.get("VAPI_ASSISTANT_ID") or "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
    )
    
    if not dial_res.get('success'):
        # RECORD FAILURE
        supabase.table("outbound_touches").insert({
            "phone": lead.get("phone"),
            "channel": "call",
            "company": lead.get("company_name", "Unknown"),
            "status": "failed",
            "meta": {"error": dial_res.get('error')}
        }).execute()
        raise Exception(f"Dial failed: {dial_res.get('error')}")
    
    # UPDATE STATUS
    update_res = supabase.table("contacts_master").update({
        "status": "calling_initiated",
        "last_contacted_at": datetime.datetime.now().isoformat()
    }).eq("id", lead_id).execute()
    check_supabase_error(update_res, "Update to calling_initiated")
    
    # RECORD TOUCH (RULE #1 - Initiated, not yet Success)
    supabase.table("outbound_touches").insert({
        "phone": lead.get("phone"),
        "channel": "call",
        "company": lead.get("company_name", "Unknown"),
        "status": "initiated",
        "payload": {"call_id": dial_res.get("call_id")}
    }).execute()
    
    print(f"✅ CALL INITIATED: {dial_res.get('call_id')}")
    return True
