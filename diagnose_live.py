
import requests
import json

BASE_URL = "https://nearmiss1193-afk--dash-v1.modal.run"

endpoints = [
    "/api/stats",
    "/api/leads",
    "/api/geo",
    "/api/logs"
]

def probe():
    print(f"--- PROBING LIVE DEPLOYMENT: {BASE_URL} ---")
    
    for ep in endpoints:
        url = BASE_URL + ep
        try:
            print(f"\n[GET] {ep}...")
            resp = requests.get(url, timeout=10)
            print(f"STATUS: {resp.status_code}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    preview = json.dumps(data)[:100]
                    print(f"DATA: {preview}...")
                except:
                    print(f"TEXT: {resp.text[:100]}...")
            else:
                print(f"ERROR: {resp.text}")
        except Exception as e:
            print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    probe()
