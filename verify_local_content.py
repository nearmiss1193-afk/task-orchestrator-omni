
import requests

URL = "http://localhost:3000/landing/hvac.html"
print(f"Checking {URL}...")
try:
    r = requests.get(URL, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Length: {len(r.text)}")
    print("Preview:\n" + r.text[:200])
except Exception as e:
    print(f"Error: {e}")
