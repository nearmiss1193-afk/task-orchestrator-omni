import requests

url = "https://nearmiss1193--ghl-omni-automation-dashboard.modal.run"
try:
    print(f"Testing {url}...")
    res = requests.get(url, timeout=10)
    print(f"Status: {res.status_code}")
    print(f"Content Start: {res.text[:200]}")
    if res.status_code == 200:
        print("SUCCESS")
    else:
        print("FAILURE")
except Exception as e:
    print(f"ERROR: {e}")
