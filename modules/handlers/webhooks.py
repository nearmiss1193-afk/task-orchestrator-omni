import os
import json
import traceback
from datetime import datetime
from modules.database.supabase_client import get_supabase

def ghl_webhook_logic(payload: dict):
    """
    INGESTION GATEWAY LOGIC - Hardened for Deep CRM Sync (Phase 16)
    """
    try:
        if payload is None:
            return {"status": "error", "message": "payload is None"}
            
        event_type = payload.get('type')
        contact_id = payload.get('contact_id') or payload.get('id')
        
        supabase = get_supabase()
        
        # 1. LOG THE EVENT (Pulse)
        try:
            supabase.table("system_health_log").insert({
                "checked_at": datetime.now().isoformat(),
                "status": f"ghl_{event_type or 'unknown'}",
                "details": {"payload": payload}
            }).execute()
        except: pass

        # 2. HANDLE CONTACT UPDATE / INGESTION
        if event_type == 'ContactUpdate' or not event_type:
            if not contact_id:
                return {"status": "skipped", "reason": "no contact id"}
                
            contact_data = payload.get('contact') or {}
            
            full_name = payload.get('name') or contact_data.get('name', 'Unknown')
            email = payload.get('email') or contact_data.get('email')
            phone = payload.get('phone') or contact_data.get('phone')
            website = payload.get('website') or contact_data.get('website')
            tags = payload.get('tags', []) or contact_data.get('tags', [])
            
            # Status mapping based on tags
            status = "new"
            if "booked" in [t.lower() for t in tags]:
                status = "booked"
            elif "not_interested" in [t.lower() for t in tags]:
                status = "trash"

            supabase.table("contacts_master").upsert({
                "ghl_contact_id": contact_id,
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "website_url": website,
                "status": status,
                "tags": tags
            }, on_conflict="ghl_contact_id").execute()
            
            return {"status": "contact_synced", "contact_id": contact_id}

        # 3. HANDLE OPPORTUNITY UPDATE (Pipeline Deep Sync)
        if event_type == 'OpportunityUpdate':
            stage_id = payload.get('stageId')
            pipeline_id = payload.get('pipelineId')
            opp_status = payload.get('status') # open, won, lost, abandoned
            
            # Map GHL stages to Supabase statuses
            sb_status = "new"
            if opp_status == "won":
                sb_status = "customer"
            elif opp_status == "lost":
                sb_status = "trash"
            
            if contact_id:
                supabase.table("contacts_master").update({
                    "status": sb_status,
                    "pipeline_stage": stage_id
                }).eq("ghl_contact_id", contact_id).execute()
                
                # Zero-Touch Onboarding Trigger
                if sb_status == "customer":
                    try:
                        from deploy import zero_touch_onboarding
                        print(f"🚀 GHL Webhook: Spawning Zero-Touch Onboarding for {contact_id}")
                        zero_touch_onboarding.spawn(contact_id)
                    except Exception as ze:
                        print(f"⚠️ Failed to spawn Zero-Touch Onboarding: {ze}")
                
            return {"status": "opportunity_synced", "contact_id": contact_id, "stage": stage_id}

        return {"status": "ignored", "type": event_type}
    except Exception as e:
        print(f"❌ GHL WEBHOOK ERROR: {e}")
        traceback.print_exc()
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
