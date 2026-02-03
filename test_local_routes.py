
from app import app
import json

client = app.test_client()

def test_routes():
    # Test Health
    res = client.get('/health')
    print(f"Health: {res.status_code}")
    
    # Test Bridge (Unauthorized)
    res = client.get('/bridge/performance')
    print(f"Bridge (No Token): {res.status_code}")
    
    # Test Bridge (Authorized)
    res = client.get('/bridge/performance', headers={"X-Sovereign-Token": "sov-audit-2026-ghost"})
    print(f"Bridge (With Token): {res.status_code}")
    if res.status_code == 200:
        print(f"Data: {res.get_json().get('timestamp')}")
    else:
        print(f"Bridge Error: {res.text}")

if __name__ == "__main__":
    test_routes()
