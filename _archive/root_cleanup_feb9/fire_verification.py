
import os
import requests
from modules.database.supabase_client import get_supabase

def fire_verification():
    supabase = get_supabase()
    email = "seaofdiscipline@gmail.com"
    name = "Sea of Discipline (Verification)"
    
    print(f"🚀 VERIFICATION: Preparing {email}...")
    
    # 1. Upsert lead into contacts_master
    lead_data = {
        "email": email,
        "full_name": name,
        "status": "verification_pending",
        "source": "manual_verification"
    }
    
    try:
        # We search first to get ID if exists
        curr = supabase.table("contacts_master").select("id").eq("email", email).execute()
        if curr.data:
            lead_id = curr.data[0]['id']
            supabase.table("contacts_master").update(lead_data).eq("id", lead_id).execute()
        else:
            res = supabase.table("contacts_master").insert(lead_data).execute()
            lead_id = res.data[0]['id']
            
        print(f"✅ Lead Ready: {lead_id}")
        
        # 2. Trigger GHL Webhook Directly (Bypass Modal for instant verification)
        # Note: In production, Modal does this, but we test the relay path here.
        webhook_url = os.environ.get("GHL_EMAIL_WEBHOOK_URL")
        if not webhook_url:
            print("❌ Error: GHL_EMAIL_WEBHOOK_URL missing in local env")
            return
            
        payload = {
            "email": email,
            "first_name": "Sea of",
            "last_name": "Discipline",
            "subject": "Sovereign Empire: Outreach Verification",
            "body": "This is a manual verification touch to confirm the Sovereign GHL Webhook Relay is ACTIVE."
        }
        
        print(f"📡 Blasting to GHL Webhook: {webhook_url}")
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Webhook accepted by GHL.")
            # 3. Log the touch for database truth
            supabase.table("outbound_touches").insert({
                "phone": "VE-RI-FY",
                "channel": "email",
                "company": "Sovereign Verification",
                "status": "sent_verified"
            }).execute()
        else:
            print(f"❌ Webhook failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    fire_verification()
