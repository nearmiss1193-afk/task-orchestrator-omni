"""
MISSION: INSTANT RESPONSE WORKER
Triggers AI responses based on GHL tag changes ('ai_reply_requested')
"""
import modal
from core.image_config import image, VAULT
from core.apps import engine_app as app

@app.function(image=image, secrets=[VAULT], schedule=modal.Cron("*/2 * * * *"))
def tag_triggered_ai_response():
    """
    Checks for contacts with 'ai_reply_requested' tag and fires response.
    Bypasses webhook delays for mission-critical speed.
    """
    print("🤖 AI WORKER: Checking for tag-triggered requests...")
    from modules.database.supabase_client import get_supabase
    import requests
    import os
    import json

    supabase = get_supabase()
    location_id = os.environ.get("GHL_LOCATION_ID")
    api_token = os.environ.get("GHL_API_TOKEN")

    if not location_id or not api_token:
        print("❌ Error: Missing credentials")
        return

    # 1. Fetch contacts with the specific tag
    # Note: GHL V2 Contacts API allows filtering by tags
    url = f"https://services.leadconnectorhq.com/contacts/?locationId={location_id}&tags=ai_reply_requested"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        contacts = response.json().get("contacts", [])
        
        if not contacts:
            print("📭 No pending tag-triggered requests.")
            return

        print(f"🎯 Found {len(contacts)} contacts requesting AI reply.")

        for contact in contacts:
            contact_id = contact.get("id")
            email = contact.get("email")
            
            # 2. Generate AI Response (Sarah TONE)
            # We use the 'intent' from the last message if possible, or a generic nudge
            ai_message = "Hey! Sarah here. I saw you had a question - I'm just looking into that for you now. Are you around for a quick chat?"
            
            # 3. Fire Response via SMS Webhook (Aggressive Speed)
            sms_hook = os.environ.get("GHL_SMS_WEBHOOK_URL")
            if sms_hook:
                payload = {
                    "contact_id": contact_id,
                    "message": ai_message
                }
                requests.post(sms_hook, json=payload, timeout=10)
                print(f"✅ AI Response sent to {contact_id}")

            # 4. Remove Tag to prevent loops
            remove_tag_url = f"https://services.leadconnectorhq.com/contacts/{contact_id}/tags"
            remove_payload = {"tags": ["ai_reply_requested"]}
            requests.delete(remove_tag_url, headers=headers, json=remove_payload, timeout=10)
            print(f"🧹 Cleaned tag for {contact_id}")

    except Exception as e:
        print(f"❌ Worker Failure: {e}")

if __name__ == "__main__":
    tag_triggered_ai_response.remote()
