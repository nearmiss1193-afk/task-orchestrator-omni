#!/usr/bin/env python3
"""
Delete old Modal apps to free up cron job slots.
Modal free tier has 5 cron job limit across all apps.
"""
import subprocess
import json

print("=" * 60)
print("MODAL APP CLEANUP - Free up cron job slots")
print("=" * 60)

# List all apps
result = subprocess.run(
    ["python", "-m", "modal", "app", "list", "--json"],
    capture_output=True, text=True
)

if result.returncode != 0:
    print(f"Error listing apps: {result.stderr}")
    exit(1)

try:
    apps = json.loads(result.stdout)
except:
    print("Could not parse app list. Raw output:")
    print(result.stdout)
    exit(1)

print(f"\nFound {len(apps)} apps:\n")

keep_apps = ["empire-api-v3"]  # Apps to KEEP
delete_candidates = []

for app in apps:
    app_name = app.get("Name", "unknown")
    app_id = app.get("App ID", "unknown")
    state = app.get("State", "unknown")
    
    print(f"  - {app_name} ({state}) [ID: {app_id}]")
    
    if app_name not in keep_apps and state == "deployed":
        delete_candidates.append(app_name)

print(f"\n\nApps to DELETE (not in keep list): {delete_candidates}")

if not delete_candidates:
    print("\nNo apps to delete. The cron limit issue may be from schedules in empire-api-v3 itself.")
    print("Check: https://modal.com/apps to see scheduled functions")
else:
    print("\nAttempting to stop old apps...")
    for app_name in delete_candidates:
        print(f"\n  Stopping {app_name}...")
        stop_result = subprocess.run(
            ["python", "-m", "modal", "app", "stop", app_name],
            capture_output=True, text=True
        )
        if stop_result.returncode == 0:
            print(f"    ✓ Stopped {app_name}")
        else:
            print(f"    ✗ Failed: {stop_result.stderr}")

print("\n" + "=" * 60)
print("Done. Now try deploying again:")
print("  python -m modal deploy modal_orchestrator_v3.py")
print("=" * 60)
