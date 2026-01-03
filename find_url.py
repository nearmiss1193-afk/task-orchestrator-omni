
import requests

base = "nearmiss1193--ghl-omni-automation-dashboard-cloud"
variants = [
    f"https://{base}-dashboard-app.modal.run",
    f"https://{base}-dashboard-app-web.modal.run",
    f"https://{base}.modal.run"
]

print("Checking URLs...")
for url in variants:
    try:
        print(f"Testing: {url}")
        res = requests.get(url, timeout=5)
        print(f"[{res.status_code}] {url}")
        if res.status_code == 200:
            print(">>> FOUND ACTIVE URL <<<")
            print(res.text[:100])
    except Exception as e:
        print(f"Error connecting to {url}: {e}")
