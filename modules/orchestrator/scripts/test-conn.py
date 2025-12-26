import requests
import os
from dotenv import load_dotenv

load_dotenv('.env.local')

URL = "https://nearmiss1193--ghl-omni-automation-ghl-webhook.modal.run"

print(f"Testing connectivity to {URL}")
try:
    # Try a GET request first to see if it even exists
    r = requests.get(URL, timeout=10)
    print(f"GET Status: {r.status_code}")
    print(f"GET Headers: {dict(r.headers)}")
    print(f"GET Body: {r.text[:200]}")
except Exception as e:
    print(f"GET Error: {e}")

try:
    # Try POST
    r = requests.post(URL, json={"type": "ping"}, timeout=10)
    print(f"POST Status: {r.status_code}")
    print(f"POST Body: {r.text[:200]}")
except Exception as e:
    print(f"POST Error: {e}")
