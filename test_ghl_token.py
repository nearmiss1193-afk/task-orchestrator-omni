"""Test the new Empire Sentinel GHL Private Integration Token."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_ghl_token():
    token = os.getenv("GHL_API_TOKEN")
    location_id = os.getenv("GHL_LOCATION_ID")
    
    print(f"[TEST] Using Token: {token[:12]}...{token[-4:]}")
    print(f"[TEST] Location ID: {location_id}")
    
    # Test 1: Get Location Info
    url = f"https://services.leadconnectorhq.com/locations/{location_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }
    
    print("\n[TEST] Calling /locations endpoint...")
    resp = requests.get(url, headers=headers)
    print(f"[RESULT] Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"[SUCCESS] Location Name: {data.get('location', {}).get('name', 'N/A')}")
        return True
    else:
        print(f"[ERROR] Response: {resp.text[:200]}")
        return False

if __name__ == "__main__":
    success = test_ghl_token()
    print(f"\n[FINAL] Token Valid: {success}")
