
import requests

base = "nearmiss1193--ghl-omni-automation-dashboard-cloud"
variants = [
    f"https://{base}-dashboard-app.modal.run",
    f"https://{base}-dashboard-app-web.modal.run",
    f"https://{base}.modal.run"
]

results = []
print("Checking URLs...")
for url in variants:
    try:
        print(f"Testing: {url}")
        res = requests.get(url, timeout=5)
        status = f"[{res.status_code}] {url}"
        print(status)
        results.append(status)
        if res.status_code == 200:
            results.append(">>> SUCCESS BODY START <<<")
            results.append(res.text[:200])
    except Exception as e:
        results.append(f"Error {url}: {e}")

with open("url_check.txt", "w") as f:
    f.write("\n".join(results))
