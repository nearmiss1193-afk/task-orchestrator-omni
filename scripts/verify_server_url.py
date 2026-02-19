import os, requests, json
from dotenv import load_dotenv
load_dotenv(".env")
key = os.environ["VAPI_PRIVATE_KEY"]

ids = {
    "Sarah": "ae717f29-6542-422f-906f-ee7ba6fa0bfe",
    "Sarah Spartan": "1a797f12-e2dd-4f7f-b2c5-08c38c74859a",
    "Rachel": "033ec1d3-e17d-4611-a497-b47cab1fdb4e"
}

for name, aid in ids.items():
    r = requests.get(f"https://api.vapi.ai/assistant/{aid}", headers={"Authorization": f"Bearer {key}"})
    d = r.json()
    srv = d.get("serverUrl", "NOT SET")
    print(f"{name}: serverUrl = {srv}")
