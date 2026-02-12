"""Debug notification pipeline: check Vapi config, recent calls, and webhook URL"""
import os
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
import requests
import json

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}'}

# 1. Check Vapi assistant serverUrl
print("=== VAPI ASSISTANT CONFIG ===")
r = requests.get('https://api.vapi.ai/assistant/1a797f12-e2dd-4f7f-b2c5-08c38c74859a', headers=headers)
d = r.json()
print(f"serverUrl: {d.get('serverUrl')}")
print(f"serverMessages: {d.get('serverMessages')}")

# 2. Check recent calls
print("\n=== RECENT VAPI CALLS ===")
r2 = requests.get('https://api.vapi.ai/call?limit=5', headers=headers)
calls = r2.json()
for c in calls:
    print(f"  Call: {c.get('id', '?')[:16]}")
    print(f"    Status: {c.get('status')}  Duration: {c.get('duration', 0)}s")
    print(f"    EndReason: {c.get('endedReason', '?')}")
    print(f"    Created: {c.get('createdAt', '?')[:19]}")
    print(f"    Customer: {c.get('customer', {}).get('number', 'unknown')}")
    print()

# 3. Check our Modal webhook endpoint
print("=== MODAL WEBHOOK CHECK ===")
# Find the actual Modal endpoint name
import subprocess
result = subprocess.run(['python', '-m', 'modal', 'app', 'list'], capture_output=True, text=True)
print(f"Modal apps: {result.stdout.strip()}")
