
import requests

variants = [
    "https://nearmiss1193-afk--dash-v1.modal.run",
    "https://nearmiss1193-afk--empire-dash-dash-v1.modal.run",
    "https://nearmiss1193--dash-v1.modal.run"
]

print("Checking Final URLs...")
for url in variants:
    try:
        print(f"Testing: {url}")
        res = requests.get(url, timeout=5)
        print(f"[{res.status_code}] {url}")
        if res.status_code == 200:
            print(">>> SUCCESS BODY START <<<")
            print(res.text[:100])
    except Exception as e:
        print(f"Error {url}: {e}")
