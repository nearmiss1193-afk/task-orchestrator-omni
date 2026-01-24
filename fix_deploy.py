
# Script to fix deploy.py corruption
import os

deploy_path = "deploy.py"

# The correct new content for lines 54-264
NEW_CONTENT = r'''@app.function(image=image, secrets=[VAULT])
@modal.fastapi_endpoint(method="POST")
async def ghl_webhook(payload: dict):
    """
    MISSION 1: GHL TWO-WAY SYNC + HYBRID DIRECTIVE
    """
    import traceback
    brain_log(f"--- WEBHOOK START ---")
    try:
        brain_log(f"Payload: {json.dumps(payload)}")
        
        type = payload.get('type')
        contact_id = payload.get('contact_id') or payload.get('id')
        
        if type == 'ContactUpdate' or not type:
            if not contact_id:
                return {"status": "skipped", "reason": "no contact id"}
                
            brain_log(f"Syncing Contact: {contact_id}")
            supabase = get_supabase()
            supabase.table("contacts_master").upsert({
                "ghl_contact_id": contact_id,
                "full_name": payload.get('name') or payload.get('contact', {}).get('name', 'Unknown'),
                "email": payload.get('email') or payload.get('contact', {}).get('email'),
                "website_url": payload.get('website') or payload.get('contact', {}).get('website'),
                "status": "new"
            }, on_conflict="ghl_contact_id").execute()
            
            # MISSION 2: VORTEX TRIGGER
            tags = payload.get('tags', []) or payload.get('contact', {}).get('tags', [])
            if 'trigger-vortex' in [t.lower() for t in tags]:
                brain_log(f"Vortex Triggered for {contact_id}")
                research_lead_logic.spawn(contact_id)
                return {"status": "vortex_triggered", "contact_id": contact_id}
                
            return {"status": "synced", "contact_id": contact_id}

        elif type == 'InboundMessage':
            brain_log(f"Inbound Message detected for {contact_id}")
            # ... spartan logic ...
            contact_obj = payload.get('contact', {}) or {}
            tags = contact_obj.get('tags', [])
            if 'candidate' in [t.lower() for t in tags] or 'hiring' in [t.lower() for t in tags]:
                return await _hiring_spartan_logic(payload)
            return await _spartan_responder_logic(payload)

        elif type == 'CallStatus':
            status = payload.get('status', '').lower()
            brain_log(f"Call Status Update: {contact_id} -> {status}")
            if status in ['no-answer', 'busy', 'voicemail', 'failed']:
                brain_log(f"🛑 Missed Call Detected for {contact_id}. Triggering Spartan Text-Back.")
                # Construct a mock payload for spartan to react to
                mock_payload = {
                    "contact_id": contact_id,
                    "message": {
                        "body": "[SYSTEM ALERT: PROSPECT MISSED A CALL. SEND TEXT BACK IMMEDIATELY]",
                        "provider": "sms"
                    }
                }
                # Use spawn to fire and forget (or await if we want speed)
                spartan_responder.spawn(mock_payload)
                return {"status": "missed_call_handled"}

        return {"status": "ignored", "type": type}
    except Exception as e:
        error_msg = f"ERR: {str(e)}\n{traceback.format_exc()}"
        brain_log(error_msg)
        return {"status": "error", "message": error_msg}

@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
async def stripe_webhook(request: Request):
    """
    WEBHOOK: STRIPE PAYMENTS
    Updates lead status to 'customer' upon payment success.
    """
    importstripe_library = __import__("stripe") # Use local var to avoid shadowing if needed, or just import stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        if webhook_secret and sig_header:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            # Dev/Test Fallback
            import json
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except Exception as e:
        return {"status": "error", "message": f"Webhook Error: {str(e)}"}

    # Handle Events
    email = None
    amount = 0.0

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        amount = intent['amount'] / 100.0
        email = intent.get('receipt_email') 

    elif event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        email = session.get('customer_details', {}).get('email')
        amount = (session.get('amount_total') or 0) / 100.0

    if email:
        print(f"💰 Payment: ${amount} from {email}")
        supabase = get_supabase()
        
        # 1. Check if contact exists
        res = supabase.table("contacts_master").select("*").eq("email", email).execute()
        contact = res.data[0] if res.data else None
        
        if contact:
            # 2. Update to Customer
            supabase.table("contacts_master").update({
                "status": "customer",
                "last_order_value": amount,
                "notes": f"{contact.get('notes', '')}\n[System] Active Customer ${amount}"
            }).eq("id", contact['id']).execute()
            
            # 3. Log
            brain_log(f"🎉 NEW CUSTOMER: {email} (${amount})")
        else:
            # Optional: Create Walk-in customer
            brain_log(f"💰 Walk-in Payment: {email} (${amount}) - Not in DB")

    return {"status": "success"}

'''

with open(deploy_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines are 0-indexed in list, but 1-indexed in file logic.
# We want to keep lines 1-53 (indices 0-52).
# We want to delete lines 54-264 (indices 53-263).
# We want to keep lines 265+ (indices 264+).

# Check if file looks as expected
line_54_start = lines[53].strip() 
line_265_start = lines[264].strip()

print(f"Line 54 starts with: '{line_54_start}'")
print(f"Line 265 starts with: '{line_265_start}'")

if not line_54_start.startswith("@app.function"):
    print("Warning: Line 54 does not start with @app.function")
if not line_265_start.startswith("def run_predator_vision"):
    print("Warning: Line 265 does not start with def run_predator_vision")

# Splicing
new_lines = lines[:53] + [NEW_CONTENT + "\n\n"] + lines[264:]

with open(deploy_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully rewrote deploy.py")
