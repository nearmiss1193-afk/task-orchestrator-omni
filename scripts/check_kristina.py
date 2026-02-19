import os, requests, json
from dotenv import load_dotenv
load_dotenv(".env")
key = os.environ["VAPI_PRIVATE_KEY"]
r = requests.get("https://api.vapi.ai/call", headers={"Authorization": f"Bearer {key}"}, params={"limit": 15})
calls = r.json()
out = []
for c in calls:
    info = {
        "id": c.get("id", ""),
        "status": c.get("status", ""),
        "endedReason": c.get("endedReason", ""),
        "customer": c.get("customer", {}).get("number", "inbound"),
        "createdAt": c.get("createdAt", ""),
        "transcript": (c.get("transcript", "") or "")[:600],
        "summary": (c.get("analysis", {}).get("summary", "") if c.get("analysis") else "")[:300]
    }
    out.append(info)

with open("scripts/all_recent_calls.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"Saved {len(out)} calls")
