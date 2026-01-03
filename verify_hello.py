
import requests
print("Checking Hello Endpoint...")
try:
    r = requests.get("https://nearmiss1193-afk--hello.modal.run", timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content: {r.text}")
except Exception as e:
    print(f"Error: {e}")
