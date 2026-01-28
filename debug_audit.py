
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROK_KEY = os.environ.get("GROK_API_KEY")
print(f"Grok Key Present: {bool(GROK_KEY)}")

files_to_read = [
    "deploy_v2.py",
    "core/image_config.py",
    "workers/research.py",
    "workers/outreach.py",
    "workers/pulse_scheduler.py",
    "utils/error_handling.py",
    "api/webhooks.py"
]

CODE = ""
for fname in files_to_read:
    with open(fname, "r") as f: CODE += f.read()

url = "https://api.x.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {GROK_KEY}", "Content-Type": "application/json"}
data = {"model": "grok-beta", "messages": [{"role": "user", "content": f"AUDIT THIS:\n{CODE[:1000]}"}]}

print("Testing Grok...")
try:
    res = requests.post(url, headers=headers, json=data)
    print(res.status_code)
    print(res.text[:500])
except Exception as e:
    print(e)
