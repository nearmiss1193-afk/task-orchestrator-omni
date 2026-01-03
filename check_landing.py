
import requests

url = "https://nearmiss1193-afk--ghl-omni-automation-hvac-landing.modal.run"
print(f"Checking {url}...")
try:
    res = requests.get(url, timeout=10)
    print(f"Status: {res.status_code}")
    print(f"Content Length: {len(res.text)}")
    print(f"Preview: {res.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
