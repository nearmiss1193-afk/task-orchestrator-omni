"""List and DELETE all Modal apps to clear workspace"""
import subprocess
import json

def list_apps():
    result = subprocess.run(['python', '-m', 'modal', 'app', 'list', '--json'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error listing apps: {result.stderr}")
        return []
    
    try:
        apps = json.loads(result.stdout)
        return apps
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw output: {result.stdout[:500]}")
        return []

def stop_app(app_name):
    """Stop an app using modal app stop"""
    print(f"  Stopping: {app_name}")
    result = subprocess.run(['python', '-m', 'modal', 'app', 'stop', app_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"    ✓ Stopped")
        return True
    else:
        # Try with --force flag
        result2 = subprocess.run(['python', '-m', 'modal', 'app', 'stop', '--confirm', app_name], capture_output=True, text=True)
        if result2.returncode == 0:
            print(f"    ✓ Stopped with force")
            return True
        print(f"    ✗ Failed: {result.stderr[:100]}")
        return False

if __name__ == "__main__":
    apps = list_apps()
    print(f"Found {len(apps)} Modal apps:\n")
    
    for app in apps:
        app_id = app.get('App ID', 'unknown')
        name = app.get('Name', 'unnamed')
        state = app.get('State', 'unknown')
        print(f"  - {name}")
        print(f"    ID: {app_id}")
        print(f"    State: {state}")
        print()
    
    # Stop ALL apps (even the stopped ones, they still hold cron quota)
    print("\n--- STOPPING ALL APPS ---\n")
    for app in apps:
        name = app.get('Name')
        if name:
            stop_app(name)
        else:
            # Try with ID
            app_id = app.get('App ID')
            if app_id:
                stop_app(app_id)
    
    print("\n--- CLEANUP COMPLETE ---")
    print("Now try: python -m modal deploy modal_orchestrator_v3.py")
