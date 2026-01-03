
import requests

url = "https://nearmiss1193--ghl-omni-automation-dashboard-minimal-web.modal.run"
print(f"Testing: {url}")
try:
    res = requests.get(url, timeout=10)
    print(f"Status: {res.status_code}")
    print(f"Content: {res.text[:100]}")
except Exception as e:
    print(f"Error: {e}")
