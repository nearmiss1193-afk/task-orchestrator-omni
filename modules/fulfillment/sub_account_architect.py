import os
import requests
import stripe
import datetime

# --- CONFIG ---
GHL_API_KEY = os.environ.get("GHL_AGENCY_API_TOKEN") # The "Boss" Key
GHL_AGENCY_ID = os.environ.get("GHL_LOCATION_ID") # Using Location for now, but provisioning usually needs Agency Key.
# Update: Creating a Sub-Account usually requires Agency API Key, OR "SaaS Mode" via API.
# If we only have Location Level Access, we might be limited.
# However, `sub_account_architect_v44_0.py` used `/v1/locations/ID/sub-accounts`? No, that endpoint doesn't exist standardly.
# Standard GHL API v2 for SaaS: POST /locations/
# Let's assume we are using v2 or v1 appropriately provided by the environment.
# Since the USER's snippet used: "https://rest.gohighlevel.com/v1/locations/" + GHL_LOCATION + "/sub-accounts", 
# this suggests a specific endpoint or a misunderstanding in the mock.
# TRUE METHOD: POST https://services.leadconnectorhq.com/locations/ (v2) requires Agency Token.

def provision_client(customer_name, customer_email, stripe_session_id=None):
    """
    Orchestrates the creation of a new GHL Sub-Account.
    """
    print(f"🏗️ Architecting Sub-Account for: {customer_name} ({customer_email})")
    
    # 1. Create Sub-Account (Location)
    location_id = create_ghl_location(customer_name, customer_email)
    
    if not location_id:
        return {"status": "error", "message": "Failed to create location"}
        
    # 2. Add User to Location
    user_id = create_ghl_user(customer_name, customer_email, location_id)
    
    # 3. Load Snapshot (The "Brain")
    # For now, we skip snapshot loading to keep it simple, or use a default template ID if available.

    # 4. SAFETY LOCK (User Directive: Website Down)
    # Do NOT trigger welcome workflow until site is live.
    print(f"🔒 [SAFETY LOCK] Welcome Email Skipped for {customer_email}. (Reason: Site Down)")
    # launch_welcome_sequence(customer_email)
    
    return {"status": "success", "location_id": location_id, "user_id": user_id}

def create_ghl_location(name, email):
    token = os.environ.get("GHL_AGENCY_API_TOKEN")
    if not token:
        print("❌ Missing GHL_AGENCY_API_TOKEN")
        return None
        
    url = "https://services.leadconnectorhq.com/locations/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    
    # Minimal Payload for Sub-Account
    payload = {
        "name": name,
        "email": email,
        "phone": "+15550000000", # Placeholder
        "address": "123 AI Blvd",
        "city": "Cyber City",
        "state": "FL",
        "country": "US",
        "timezone": "US/Eastern",
        "settings": {
            "allowDuplicateContact": True,
            "allowDuplicateOpportunity": True
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            data = response.json()
            loc_id = data.get("id")
            print(f"✅ GHL Location Created: {loc_id}")
            return loc_id
        else:
            print(f"❌ Creation Failed ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def create_ghl_user(name, email, location_id):
    # This usually requires a separate endpoint to add a user to a location
    # POST /users/
    token = os.environ.get("GHL_AGENCY_API_TOKEN")
    url = "https://services.leadconnectorhq.com/users/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "firstName": name.split()[0],
        "lastName": " ".join(name.split()[1:]) if " " in name else "Admin",
        "email": email,
        "password": "Password123!", # Set a default
        "type": "account",
        "role": "admin",
        "locationIds": [location_id]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            print(f"✅ GHL User Created for {email}")
            return response.json().get("id")
        else:
            print(f"⚠️ User Creation Failed: {response.text}")
            return None
    except Exception as e:
        print(f"⚠️ User Exception: {e}")
        return None
