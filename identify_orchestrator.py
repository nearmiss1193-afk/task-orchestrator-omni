import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
CHECK_IDS = [
    "a3e439a2-4560-4625-99c8-222678bf130d", # From new_orchestrator_id.txt
    "033ec1d3-e17d-4611-a497-b47cab1fdb4e"  # Empire Office Manager
]

for aid in CHECK_IDS:
    url = f"https://api.vapi.ai/assistant/{aid}"
    headers = {"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"}
    print(f"Checking ID: {aid}...")
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        print(f"✅ NAME: {data.get('name')}")
        print(f"PROMPT: {data.get('model', {}).get('systemPrompt', '')[:200]}...")
    else:
        print(f"❌ Failed: {res.status_code} | {res.text}")
    print("-" * 20)
