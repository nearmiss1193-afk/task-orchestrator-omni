import os
import json
import traceback
from datetime import datetime
from modules.database.supabase_client import get_supabase

def ghl_webhook_logic(payload: dict):
    """
    INGESTION GATEWAY LOGIC
    """
    try:
        if payload is None:
            return {"status": "error", "message": "payload is None"}
            
        type = payload.get('type')
        contact_id = payload.get('contact_id') or payload.get('id')
        
        if type == 'ContactUpdate' or not type:
            if not contact_id:
                return {"status": "skipped", "reason": "no contact id"}
                
            supabase = get_supabase()
            contact_data = payload.get('contact') or {}
            
            full_name = payload.get('name') or contact_data.get('name', 'Unknown')
            email = payload.get('email') or contact_data.get('email')
            website = payload.get('website') or contact_data.get('website')
            
            supabase.table("contacts_master").upsert({
                "ghl_contact_id": contact_id,
                "full_name": full_name,
                "email": email,
                "website_url": website,
                "status": "new"
            }, on_conflict="ghl_contact_id").execute()
            
            return {"status": "synced", "contact_id": contact_id}

        return {"status": "ignored", "type": type}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def stripe_webhook_logic(payload_bytes: bytes, sig_header: str):
    """
    PAYMENT GATEWAY LOGIC
    """
    import stripe
    # Note: Logic moved from deploy.py, simplified for modularity
    try:
        event = json.loads(payload_bytes)
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_email = session.get('customer_details', {}).get('email')
            # Provisioning logic should be here or calls another module
            return {"status": "success", "customer": customer_email}
        return {"status": "received"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
