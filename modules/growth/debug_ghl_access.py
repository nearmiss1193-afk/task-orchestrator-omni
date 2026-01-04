
import os
import requests
from dotenv import load_dotenv

env_path = os.path.join(os.getcwd(), '.env')
load_dotenv(env_path)

def debug_access():
    print("🕵️ Debugging GHL Token Access...")
    
    token = os.environ.get("GHL_API_TOKEN")
    current_location = os.environ.get("GHL_LOCATION_ID")
    
    if not token:
        print("❌ ERROR: No Token in .env")
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'Version': '2021-07-28',
        'Content-Type': 'application/json'
    }

    print(f"   Current Target Location: {current_location}")
    print("   Querying accessible locations...")

    # Try 1: Get User Info / Assigned Locations
    # Note: Endpoints vary by V2 version, trying standard /locations/
    try:
        res = requests.get("https://services.leadconnectorhq.com/locations/", headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            locations = data.get('locations', [])
            print(f"   ✅ SUCCESS. Token has access to {len(locations)} locations:")
            for loc in locations:
                mark = " [CURRENT TARGET]" if loc['id'] == current_location else ""
                print(f"      - {loc['firstName']} {loc.get('lastName','')} (ID: {loc['id']}){mark}")
                
                if loc['id'] == current_location:
                    print("      ✨ MATCH FOUND! But requests still failing? Check scopes.")
        else:
            print(f"   ⚠️ API returned {res.status_code}: {res.text}")
            
    except Exception as e:
        print(f"   ❌ CRITICAL FAIL: {e}")

if __name__ == "__main__":
    debug_access()
