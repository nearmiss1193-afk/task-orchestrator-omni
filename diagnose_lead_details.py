
import requests
import urllib.parse
import json

BASE_URL = "https://nearmiss1193-afk--dash-v1.modal.run"

def probe_lead(target_id):
    # Simulate JS: encodeURIComponent(id)
    safe_id = urllib.parse.quote(target_id, safe='')
    url = f"{BASE_URL}/api/lead/{safe_id}"
    
    print(f"--- PROBING: {url} ---")
    try:
        resp = requests.get(url)
        print(f"STATUS: {resp.status_code}")
        print(f"TEXT: {resp.text[:200]}")
        try:
            print(f"JSON: {json.dumps(resp.json(), indent=2)[:500]}")
        except:
            pass
    except Exception as e:
        print(f"FAIL: {e}")

if __name__ == "__main__":
    # Test cases
    print("1. Testing 'Simpler' ID (from debug output earlier)")
    probe_lead("1harbor_turf") 
    
    print("\n2. Testing 'Chaos' ID (Simulating what might be breaking it)")
    probe_lead("Chaos Lead #1") 
    
    print("\n3. Testing 'Space' ID")
    probe_lead("Test User")
