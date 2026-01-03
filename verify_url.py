import requests
import sys

try:
    with open('ngrok.txt', 'r') as f:
        url = f.read().strip()
        
    print(f"RAW: '{url}'")
    
    # Try connecting
    try:
        r = requests.get(f"{url}/api/stats", timeout=5)
        print(f"STATUS: {r.status_code}")
        print(f"VALID_URL: {url}")
    except Exception as e:
        print(f"CONNECTION_FAILED: {e}")
        
except Exception as e:
    print(f"FILE_ERROR: {e}")
