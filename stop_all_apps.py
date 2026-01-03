
import re
import subprocess

with open("apps_utf8.txt", "r", encoding="utf-8") as f:
    content = f.read()
    
ids = re.findall(r"ap-[A-Za-z0-9]+", content)
print(f"Found {len(ids)} apps. Stopping them...")

for app_id in ids:
    print(f"Stopping {app_id}...")
    res = subprocess.run(["python", "-m", "modal", "app", "stop", app_id], capture_output=True, text=True, encoding='utf-8')
    with open("stop_log.txt", "a", encoding="utf-8") as log:
        log.write(f"--- {app_id} ---\n")
        log.write(res.stdout + "\n")
        log.write(res.stderr + "\n")
    print(f"Result: RC={res.returncode}")
    
print("✅ All apps processed. Check stop_log.txt")
