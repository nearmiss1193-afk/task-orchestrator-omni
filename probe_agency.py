
import modal
import deploy
import requests
import json
import os

app = deploy.app

@app.local_entrypoint()
def main():
    print("🕵️‍♂️ AGENCY TOKEN SCOPE PROBE")
    res = probe_agency.remote()
    print(res)

@app.function(image=deploy.image, secrets=[deploy.VAULT])
def probe_agency():
    token = os.environ.get("GHL_AGENCY_API_TOKEN")
    if not token: return "No Agency Token"
    
    headers = {
        'Authorization': f'Bearer {token}', 
        'Version': '2021-07-28', 
        'Content-Type': 'application/json'
    }
    
    logs = []
    
    # 1. Try /users/me again with debug
    try:
        r = requests.get("https://services.leadconnectorhq.com/users/me", headers=headers)
        logs.append(f"ME Check: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        logs.append(f"ME Error: {e}")

    # 2. Try Listing Locations (Agency Level)
    try:
        r = requests.get("https://services.leadconnectorhq.com/locations/?limit=1", headers=headers)
        logs.append(f"LOC List Check: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            locs = data.get('locations', [])
            if locs:
                l = locs[0]
                logs.append(f"✅ Found Location: {l.get('id')} / {l.get('name')}")
                logs.append(f"   Company ID from Loc: {l.get('companyId')}") # This is valid?
            else:
                logs.append("No locations found (Empty list)")
        else:
            logs.append(f"LOC List Fail: {r.text[:100]}")
    except Exception as e:
         logs.append(f"LOC Error: {e}")

    return "\n".join(logs)
