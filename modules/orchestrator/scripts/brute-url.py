import requests
import os

URLS = [
    "https://nearmiss1193--ghl-omni-automation-ghl-webhook.modal.run",
    "https://nearmiss1193-ghl-omni-automation-ghl-webhook.modal.run",
    "https://nearmiss1193--ghl-omni-automation.modal.run/ghl_webhook",
    "https://nearmiss1193--ghl-omni-automation.modal.run",
    "https://nearmiss1193--ghl-omni-automation-ghl-webhook-dev.modal.run",
]

for url in URLS:
    print(f"Testing {url}...")
    try:
        r = requests.post(url, json={"type": "ping"}, timeout=5)
        print(f"  Status: {r.status_code}")
        if r.status_code != 404:
            print(f"  SUCCESS! (or at least not 404)")
    except Exception as e:
        print(f"  Error: {e}")
