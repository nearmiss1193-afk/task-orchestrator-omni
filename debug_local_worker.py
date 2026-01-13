import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Config from .env
APOLLO_KEY = os.environ.get("APOLLO_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")

print(f"Apollo Key Present: {bool(APOLLO_KEY)}")
print(f"Supabase URL: {SUPABASE_URL}")

def supabase_request(method, table, data=None, params=None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k,v in params.items()])
    
    try:
        print(f"Supabase {method} {url}")
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PATCH":
            r = requests.patch(url, headers=headers, json=data, timeout=30)
        print(f"Status: {r.status_code}")
        if not r.ok:
            print(r.text)
        return r.json() if r.ok else None
    except Exception as e:
        print(f"Supabase Error: {e}")
        return None

def test_prospect():
    print("\n--- Testing Prospecting ---")
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_KEY
    }
    payload = {
        "q_keywords": "HVAC contractor",
        "organization_locations": ["Florida"],
        "per_page": 2
    }
    try:
        r = requests.post("https://api.apollo.io/v1/organizations/search", json=payload, headers=headers)
        print(f"Apollo Response: {r.status_code}")
        if r.ok:
            data = r.json()
            orgs = data.get("organizations", [])
            print(f"Found {len(orgs)} orgs")
            if orgs:
                print(f"Sample: {orgs[0].get('name')}")
        else:
            print(r.text)
    except Exception as e:
        print(f"Apollo Error: {e}")

def test_outreach_check():
    print("\n--- Testing Lead Check ---")
    leads = supabase_request("GET", "leads", params={"status": "eq.new", "limit": "5"})
    print(f"Found {len(leads) if leads else 0} new leads in Supabase")

def test_auth():
    print("\n--- Testing Apollo Auth ---")
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_KEY
    }
    try:
        r = requests.get("https://api.apollo.io/v1/auth/health", params={"api_key": APOLLO_KEY}, headers=headers)
        print(f"Auth Response via Param: {r.status_code}")
        print(r.text)

        r2 = requests.get("https://api.apollo.io/v1/auth/health", headers=headers)
        print(f"Auth Response via Header: {r2.status_code}")
        print(r2.text)
    except Exception as e:
        print(f"Auth Error: {e}")

if __name__ == "__main__":
    test_auth()
    test_outreach_check()
    # test_prospect()
