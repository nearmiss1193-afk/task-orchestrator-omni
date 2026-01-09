"""Test GHL API with different version headers and token formats."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_all_versions():
    token = os.getenv("GHL_API_TOKEN")
    location_id = os.getenv("GHL_LOCATION_ID")
    
    print(f"Token: {token}")
    print(f"Location: {location_id}\n")
    
    # Test different API version headers
    versions = ["2021-07-28", "2021-04-15", None]
    
    for version in versions:
        print(f"\n=== Testing Version: {version} ===")
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        if version:
            headers["Version"] = version
        
        # Test contacts endpoint
        url = f"https://services.leadconnectorhq.com/contacts/?locationId={location_id}&limit=1"
        resp = requests.get(url, headers=headers)
        print(f"Contacts: {resp.status_code}")
        if resp.status_code != 200:
            print(f"  Error: {resp.text[:150]}")
        else:
            print(f"  Data: {resp.json()}")
            
    # Also test with different auth header format
    print("\n=== Testing with 'Api-Key' header ===")
    headers = {
        "Api-Key": token,
        "Accept": "application/json"
    }
    url = f"https://services.leadconnectorhq.com/contacts/?locationId={location_id}&limit=1"
    resp = requests.get(url, headers=headers)
    print(f"Contacts: {resp.status_code}")
    if resp.status_code != 200:
        print(f"  Error: {resp.text[:150]}")
    else:
        print(f"  SUCCESS! Data: {resp.json()}")

if __name__ == "__main__":
    test_all_versions()
