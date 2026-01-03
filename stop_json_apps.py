
import json
import subprocess

with open("apps.json", "r") as f:
    apps = json.load(f)
    
print(f"Found {len(apps)} apps.")

for app in apps:
    app_id = app.get("App ID")
    name = app.get("Description")
    print(f"Stopping {name} ({app_id})...")
    res = subprocess.run(["python", "-m", "modal", "app", "stop", app_id], capture_output=True, text=True, encoding='utf-8')
    print(f"RC: {res.returncode}")
    if res.returncode != 0:
        print(f"Error: {res.stderr}")

print("✅ Purge Complete.")
