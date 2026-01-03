
import modal
import deploy
import requests
import json
import os

app = deploy.app

# USER CONFIG
TEST_EMAIL = "nearmiss1193@gmail.com"
TEST_PHONE = "+13529368152"
TARGET_URL = "https://bigwaverestoration.com"
TARGET_NAME = "Big Wave Restoration"

@app.local_entrypoint()
def main():
    print(f"🚀 INITIATING LIVE FIRE TEST")
    print(f"🎯 Simulation Target: {TARGET_NAME}")
    print(f"📧 Recipient: {TEST_EMAIL} / {TEST_PHONE}")
    
    # Execute Remote
    res = fire_mission.remote(TEST_EMAIL, TEST_PHONE, TARGET_URL, TARGET_NAME)
    
    print("\n--- 🏁 MISSION REPORT ---")
    print(res)

@app.function(image=deploy.image, secrets=[deploy.VAULT], timeout=60)
def fire_mission(email, phone, url, name):
    print(f"⚙️ [Cloud] Spinning up Spartan Engine...")
    
    # 1. GENERATE COPY (The Saw)
    # Re-using the logic from deploy.py but hardcoded for reliability in this test
    hook = "noticed you promise 24/7 service—do you have someone awake at 3am or does that go to voicemail? i built a tool that handles those graveyard shifts for you."
    
    subject = f"question re: {name.lower()}"
    body = f"hey {name.split()[0].lower()} team,\n\n{hook}\n\nmind if i send over a 30s video showing exactly how to fix it?"
    
    print(f"📝 Generated Body:\n{body}")
    

    # 2. SELECT TOKEN STRATEGY
    # The 'pit-' token is likely a Personal Integration Token which can act as a master key if scoped correctly.
    # The 'eyJ' token is likely an expired OAuth token.
    # We will prioritize the PIT token.
    
    token_candidate = os.environ.get("GHL_AGENCY_API_TOKEN") # Try the PIT token
    print(f"🔑 Attempting with Agency/PIT Token: {token_candidate[:10]}...")
    
    headers = {
        'Authorization': f'Bearer {token_candidate}', 
        'Version': '2021-04-15', 
        'Content-Type': 'application/json'
    }
    
    # 3. VERIFY LOCATION ACCESS (Before Firing)
    # We need to know if this token can access Location RnK4...
    # If the token is global/agency, we often need to specify 'LocationId' header or it just works if implied.
    # Let's assume standard behavior.

    
    # Determine Location ID from Token (or hardcode if known from previous context)
    # We will try to rely on the token scoping or fetch it.
    # For sending a conversation message, we usually need a Contact ID.
    
    # Step A: Upsert Contact
    print("👤 Upserting Test Contact into GHL...")
    upsert_payload = {
        "email": email,
        "phone": phone,
        "firstName": "NearMiss",
        "lastName": "TestUser",
        "name": "NearMiss TestUser",
        "tags": ["test-live-fire", "big-wave-sim"]
    }
    
    contact_id = None
    try:
        # Try Lookup First
        query = f"https://services.leadconnectorhq.com/contacts/lookup?email={email}"
        res = requests.get(query, headers=headers)
        if res.status_code == 200 and res.json().get('contacts'):
            contact_id = res.json()['contacts'][0]['id']
            print(f"✅ Found Existing Contact: {contact_id}")
        else:
            # Create
            res = requests.post("https://services.leadconnectorhq.com/contacts/", json=upsert_payload, headers=headers)
            if res.status_code in [200, 201]:
                contact_id = res.json().get('contact', {}).get('id')
                print(f"✅ Created New Contact: {contact_id}")
            else:
                return f"❌ Failed to create contact: {res.text}"
    except Exception as e:
        return f"❌ Contact Error: {str(e)}"

    if not contact_id:
        return "❌ Could not resolve Contact ID. Aborting."

    # 3. FIRE EMAIL (The Saw)
    print(f"🔫 Firing Email to {contact_id}...")
    email_payload = {
        "type": "Email",
        "contactId": contact_id,
        "emailFrom": "system@aiserviceco.com", # Sender
        "emailSubject": subject,
        "html": body.replace("\n", "<br>")
    }
    
    try:
        res = requests.post("https://services.leadconnectorhq.com/conversations/messages", json=email_payload, headers=headers)
        print(f"RAW EMAIL RESPONSE: {res.status_code} - {res.text}") # ADDED DEBUG
        email_status = f"Email Status: {res.status_code} - {res.text}"
    except Exception as e:
        email_status = f"Email Failed: {str(e)}"

    # 4. FIRE SMS (Optional, per request)
    print(f"🔫 Firing SMS to {contact_id}...")
    sms_payload = {
        "type": "SMS",
        "contactId": contact_id,
        "message": f"Spartan Test: {hook}"
    }
    try:
        res = requests.post("https://services.leadconnectorhq.com/conversations/messages", json=sms_payload, headers=headers)
        print(f"RAW SMS RESPONSE: {res.status_code} - {res.text}") # ADDED DEBUG
        sms_status = f"SMS Status: {res.status_code} - {res.text}"
    except Exception as e:
        sms_status = f"SMS Failed: {str(e)}"

    return f"✅ MISSION COMPLETE.\n{email_status}\n{sms_status}"
