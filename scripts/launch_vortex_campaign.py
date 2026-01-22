import json
import requests
import time
import os
from datetime import datetime

# V2 Master Fusion Endpoint (Master Version)
WEBHOOK_URL = "https://nearmiss1193-afk--v2-empire-fusion-master-orchestrate.modal.run"

def launch_campaign():
    input_file = "execution/mass_prospects_100.json"
    print(f"🚀 RELAYING PROSPECTS TO VORTEX V2 ORCHESTRATOR...")
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found.")
        return

    with open(input_file, "r") as f:
        leads = json.load(f)
        
    # V2 payload expects 'campaign' and 'action'
    # We pass the batch as part of the orchestrate request
    payload = {
        "campaign": "SMS_BLAST", # V2 support SMS_BLAST triggers
        "action": "start",
        "metadata": {
            "source": "manual_launch",
            "batch_size": len(leads)
        },
        "leads": leads # Passing leads directly for V2 bridge processing
    }
    
    try:
        print(f"-> 📡 Triggering V2 Mission with {len(leads)} leads...")
        res = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        if res.status_code == 200:
            print(f"✅ [SUCCESS] V2 Mission Initialized: {res.json().get('message')}")
        else:
            print(f"⚠️ V2 Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print(f"\n🏁 V2 CAMPAIGN UPLINK COMPLETE.")

if __name__ == "__main__":
    launch_campaign()
