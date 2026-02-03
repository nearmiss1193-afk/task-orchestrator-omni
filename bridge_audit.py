import os
import requests

url = "https://empire-unified-backup-production-6d15.up.railway.app"
token = "sov-audit-2026-ghost"

print(f"🛰️ Auditing Bridge at {url}...")

# 1. Health check
try:
    r = requests.get(f"{url}/health", headers={"X-Sovereign-Token": token}, timeout=10)
    print(f"Base /health: {r.status_code}")
except Exception as e:
    print(f"Base /health error: {e}")

# 2. Try Bridge root
try:
    r = requests.get(url, headers={"X-Sovereign-Token": token}, timeout=10)
    print(f"Base URL: {r.status_code}")
except Exception as e:
    print(f"Base URL error: {e}")

# 3. Try common endpoints
endpoints = ["/task", "/bridge/task", "/bridge/performance", "/leads"]
for ep in endpoints:
    try:
        r = requests.get(f"{url}{ep}", headers={"X-Sovereign-Token": token}, timeout=10)
        print(f"Endpoint {ep}: {r.status_code}")
    except Exception as e:
        print(f"Endpoint {ep} error: {e}")
