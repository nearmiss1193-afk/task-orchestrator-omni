
import requests
import time

try:
    print("Testing Cortex Connectivity...")
    res = requests.get("http://localhost:8000/")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}")
    
    if res.status_code == 200:
        print("✅ Cortex is ONLINE.")
    else:
        print("❌ Cortex Status Error.")
        
except Exception as e:
    print(f"❌ Cortex Connection Failed: {e}")
