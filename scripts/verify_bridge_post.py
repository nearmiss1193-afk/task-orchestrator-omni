import os
import requests
import json

URL = "https://empire-unified-backup-production-6d15.up.railway.app/bridge/task"
TOKEN = "sov-audit-2026-ghost"

print(f"🛰️ Testing Bridge POST Handshake at {URL}...")

payload = {
    "task": "Absolute Truth Handshake Verification (Phase 2.1)",
    "source": "Sovereign-Restoration-Audit"
}

headers = {
    "X-Sovereign-Token": TOKEN,
    "Content-Type": "application/json"
}

try:
    r = requests.post(URL, headers=headers, json=payload, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text}")
    
    if r.status_code == 200:
        print("✅ BRIDGE POST VERIFIED: Handshake is operational.")
    else:
        print(f"❌ BRIDGE POST FAILED: Received status {r.status_code}")
except Exception as e:
    print(f"❌ EXCEPTION during Bridge POST: {e}")
