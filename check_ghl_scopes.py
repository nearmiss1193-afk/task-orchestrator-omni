"""Check what scopes the GHL token has access to."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_token_access():
    token = os.getenv("GHL_API_TOKEN")
    location_id = os.getenv("GHL_LOCATION_ID")
    
    print(f"Token: {token[:15]}...")
    print(f"Location: {location_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }
    
    # Test various endpoints to see what works
    endpoints = [
        ("Location Info", f"https://services.leadconnectorhq.com/locations/{location_id}"),
        ("Contacts List", f"https://services.leadconnectorhq.com/contacts/?locationId={location_id}&limit=1"),
        ("Conversations", f"https://services.leadconnectorhq.com/conversations/?locationId={location_id}&limit=1"),
        ("Users", f"https://services.leadconnectorhq.com/users/?locationId={location_id}"),
    ]
    
    results = []
    for name, url in endpoints:
        resp = requests.get(url, headers=headers)
        status = "OK" if resp.status_code == 200 else f"FAIL ({resp.status_code})"
        results.append(f"{name}: {status}")
        print(f"[{status}] {name}")
        if resp.status_code != 200:
            print(f"  Error: {resp.text[:100]}")
    
    # Write results to file
    with open("ghl_scope_test.txt", "w") as f:
        f.write("GHL Token Scope Test Results\n")
        f.write("="*40 + "\n")
        for r in results:
            f.write(r + "\n")
    
    print("\nResults saved to ghl_scope_test.txt")

if __name__ == "__main__":
    check_token_access()
