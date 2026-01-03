
import modal
import os
import requests
import json
import time

# --- CONFIG ---
# We use the token from the secret, but rely on env var injection
API_VERSION = "2021-07-28"
BASE_URL = "https://services.leadconnectorhq.com"

# --- MODAL APP ---
app = modal.App("ghl-architect")
image = modal.Image.debian_slim().pip_install("requests")

# Define Secret (Redundant definition for standalone usage, matching deploy.py)
VAULT = modal.Secret.from_dict({
    "GHL_AGENCY_API_TOKEN": "pit-f5aa6520-ae89-46b2-a3ea-d53b8d862a26"
})

def _get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Version": API_VERSION,
        "Content-Type": "application/json"
    }

@app.function(image=image, secrets=[VAULT])
def create_client_infra(client_name, email, phone, address, city, state, country="US", postal_code="00000", timezone="US/Eastern", snapshot_id=None):
    """
    Provisions a new GHL account (Location) for a paying client.
    """
    print(f"🏗️ [Architect] Starting infrastructure build for: {client_name}")
    
    token = os.environ.get("GHL_AGENCY_API_TOKEN")
    if not token:
        return {"status": "error", "message": "Missing Agency Token"}

    headers = _get_headers(token)

    # 1. Fetch Company ID (Agency ID)
    # We try to get it from the user info associated with the token
    company_id = None
    try:
        user_res = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if user_res.status_code == 200:
            user_data = user_res.json()
            company_id = user_data.get('companyId')
            # Fallback if not at root
            if not company_id and 'roles' in user_data:
                for role in user_data['roles']:
                    if role.get('type') == 'agency':
                        company_id = role.get('companyId') # Structure varies, sometimes it's implied
                        
            print(f"✅ Found Company ID: {company_id}")
        else:
            print(f"⚠️ Failed to fetch User Info: {user_res.text}")
    except Exception as e:
        print(f"❌ Error fetching Company ID: {str(e)}")

    if not company_id:
        # OPTION B: List Locations and grab the companyId from the first one?
        # Only works if we have locations.
        pass

    if not company_id:
        return {"status": "error", "message": "Could not determine Company ID (Agency ID)."}

    # 2. Create Location
    payload = {
        "name": client_name,
        "phone": phone,
        "companyId": company_id,
        "address": address,
        "city": city,
        "state": state,
        "country": country,
        "postalCode": postal_code,
        "timezone": timezone,
        "website": f"https://{client_name.replace(' ', '').lower()}.com", # Placceholder
        "settings": {
            "allowDuplicateContact": True,
            "allowDuplicateOpportunity": True
        }
    }
    
    if snapshot_id:
        payload["snapshotId"] = snapshot_id

    try:
        print(f"🚀 Creating Location with Payload: {json.dumps(payload)}")
        res = requests.post(f"{BASE_URL}/locations", json=payload, headers=headers)
        
        if res.status_code in [200, 201]:
            data = res.json()
            loc_id = data.get('id')
            print(f"✅ Location Created Successfully! ID: {loc_id}")
            
            # 3. Create User for Client? (Optional, skipping for now)
            
            return {
                "status": "success", 
                "location_id": loc_id, 
                "login_url": f"https://app.gohighlevel.com/location/{loc_id}",
                "api_response": data
            }
        else:
            print(f"❌ Creation Failed: {res.text}")
            return {"status": "error", "message": res.text}
            
    except Exception as e:
        return {"status": "critical_error", "message": str(e)}

@app.local_entrypoint()
def main():
    print("🦅 Architect Standalone Mode")
    # Example Usage (Commented out to prevent accidental firing)
    # create_client_infra.remote(
    #     client_name="Test Client Alpha",
    #     email="client@example.com",
    #     phone="+15550199",
    #     address="123 Main St",
    #     city="Miami",
    #     state="FL",
    #     postal_code="33101",
    #     timezone="US/Eastern"
    # )
