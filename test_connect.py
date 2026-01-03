import requests
import json

candidates = [
    "https://jeanie-makable-deon.ngrok-free.dev",
    "https://jeanie-maakable-deon.ngrok-free.dev",
    "https://jeanible-deon.ngrok-free.dev"
]

print("Starting Probe...")
for url in candidates:
    try:
        print(f"Testing {url}...")
        r = requests.get(f"{url}/api/stats", timeout=5)
        if r.status_code == 200:
            print(f"SUCCESS MATCH: {url}")
            break
        else:
            print(f"FAILED {url}: Status {r.status_code}")
    except Exception as e:
        print(f"ERROR {url}: {e}")
print("Probe Complete")
