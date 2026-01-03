
import requests
url = "https://nearmiss1193-afk--hello-check-hello.modal.run"
print(f"Checking {url}...")
try:
    r = requests.get(url, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content: {r.text}")
except Exception as e:
    print(f"Error: {e}")
