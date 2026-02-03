
import requests
import json

# --- CONFIG ---
BRIDGE_URL = "https://empire-unified-backup-production-6d15.up.railway.app/bridge/task"
BRIDGE_TOKEN = "sov-audit-2026-ghost"

def inject_tasks():
    tasks = [
        {"task": "Verify SSL status for American Air Repair", "source": "User-Directive"},
        {"task": "Prepare 14-day AI Phone System demo for Robert Kinney", "source": "User-Directive"},
        {"task": "Follow up with bfisher@petersonmyers.com regarding CLS failure", "source": "User-Directive"}
    ]
    
    headers = {
        "X-Sovereign-Token": BRIDGE_TOKEN,
        "Content-Type": "application/json"
    }
    
    print("🚀 Injecting Tasks into Sovereign Bridge...")
    
    for t in tasks:
        try:
            res = requests.post(BRIDGE_URL, headers=headers, json=t)
            if res.status_code == 200:
                print(f"✅ Success: {t['task']} | ID: {res.json().get('task_id')}")
            else:
                print(f"❌ Failed ({res.status_code}): {t['task']}")
                print(f"   Response: {res.text}")
        except Exception as e:
            print(f"❌ Error injecting '{t['task']}': {e}")

if __name__ == "__main__":
    inject_tasks()
