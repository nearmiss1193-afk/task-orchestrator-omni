
import modal
from fastapi import Request
import os
import json
import requests
import datetime

app = modal.App("voice-nexus-vapi")

image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "uvicorn", "requests", "supabase")
)

# --- SHARED HELPERS (Ported from deploy.py) ---
def get_supabase():
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def brain_log(message: str):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    try:
        supabase = get_supabase()
        supabase.table("brain_logs").insert({"message": message, "timestamp": timestamp}).execute()
    except Exception as e:
        print(f"Failed to log to DB: {str(e)}")

def add_ghl_note_and_tag(contact_id: str, note_body: str, tag: str):
    """
    Updates GHL Contact with a Note and a Tag.
    """
    token = os.environ.get("GHL_AGENCY_API_TOKEN") # Using Agency Token (PIT)
    loc_id = os.environ.get("GHL_LOCATION_ID")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Location-Id": loc_id
    }
    
    # 1. Add Tag
    try:
        requests.post(
            f"https://services.leadconnectorhq.com/contacts/{contact_id}/tags",
            json={"tags": [tag]},
            headers=headers
        )
    except Exception as e:
        brain_log(f"⚠️ Failed to tag contact {contact_id}: {e}")

    # 2. Add Note
    try:
        requests.post(
            f"https://services.leadconnectorhq.com/contacts/{contact_id}/notes",
            json={"body": note_body},
            headers=headers
        )
    except Exception as e:
        brain_log(f"⚠️ Failed to add note to {contact_id}: {e}")


@app.function(image=image, secrets=[modal.Secret.from_name("agency-vault")])
@modal.fastapi_endpoint(method="POST")
async def voice_concierge_webhook(payload: dict):
    """
    MISSION 27: VOICE NEXUS (Inbound Call Handler)
    Handles inbound webhook events from Vapi.ai (The "Closer").
    """
    
    # Extract Call Details
    message = payload.get('message', {})
    call = message.get('call', {})
    
    # Depending on Vapi version/event type, fields move. 
    # 'end-of-call-report' is usually the key event we want.
    if message.get('type') != "end-of-call-report":
        return {"status": "ignored", "reason": "not-end-of-call"}

    customer = call.get('customer', {})
    phone = customer.get('number')
    status = call.get('status')
    
    # Extract Transcript & Summary
    transcript = message.get('transcript', "")
    analysis = message.get('analysis', {})
    summary = analysis.get('summary', 'No summary provided by AI.')
    
    brain_log(f"📞 [Voice Nexus] Call Ended | Phone: {phone} | Status: {status}")
    
    if phone:
        # Match to GHL Contact via Supabase
        supabase = get_supabase()
        
        # Normalize phone (strip +1 if needed, but loose match is safer)
        # We assume Supabase has the normalized format.
        # Helper: Normalize phone for matching
        def normalize_phone(p):
            return "".join(filter(str.isdigit, p))[-10:] # Last 10 digits

        lookup_phone = normalize_phone(phone)
        
        # 1. Try Exact Match (Fast)
        res = supabase.table("contacts_master").select("*").eq("phone", phone).execute()
        
        # 2. Try Normalized Match (Slow but robust) via Post-Processing (or improved query if possible)
        # Supabase doesn't easily do "ends_with" on encrypted/text columns without extensions.
        # We will trust the exact match first, if empty, we might need a broader search if the DB is messy.
        # For this high-tech system, we assume contacts_master is fairly clean +1 format.
        
        if not res.data:
            # Try without +1 if original had it
            if phone.startswith('+1'):
                res = supabase.table("contacts_master").select("*").eq("phone", phone[2:]).execute()
            elif not phone.startswith('+'):
                res = supabase.table("contacts_master").select("*").eq("phone", f"+1{phone}").execute()

        if res.data:
            contact = res.data[0]
            ghl_id = contact.get('ghl_contact_id')
            brain_log(f"✅ Matched Caller to Contact: {contact.get('full_name')} ({ghl_id})")
            
            # Update GHL
            note = f"🎙️ VOICE AI SUMMARY:\n{summary}\n\n---\nTranscript Preview: {transcript[:100]}..."
            add_ghl_note_and_tag(ghl_id, note, "Voice Agent Engaged")
            brain_log(f"Synced Voice Data to GHL for {ghl_id}")
            
        else:
            brain_log(f"⚠️ Unknown Caller {phone}. No existing GHL match found.")
            # OPTIONAL: Create contact here?
            # For now, we just log it.
            
    return {"status": "processed"}

@app.function(image=image)
def warm_lead_dialer(contact_id: str, phone: str):
    """
    OUTBOUND: Day 3 'Courtesy Call'
    Triggers Vapi to call the lead.
    """
    vapi_key = os.environ.get("VAPI_PRIVATE_KEY")
    assistant_id = os.environ.get("VAPI_ASSISTANT_ID")
    
    if not vapi_key or not assistant_id:
        print("❌ Missing Vapi Config")
        return {"error": "config_missing"}
    
    url = "https://api.vapi.ai/call/phone"
    headers = {
        "Authorization": f"Bearer {vapi_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "customer": {"number": phone},
        "assistantId": assistant_id
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        brain_log(f"🚀 Outbound Call Initiated to {phone}: {res.status_code}")
        return res.json()
    except Exception as e:
        brain_log(f"❌ Dial Fail: {e}")
        return {"error": str(e)}
