import os, requests, json
from dotenv import load_dotenv
load_dotenv(".env")
key = os.environ["VAPI_PRIVATE_KEY"]
r = requests.get("https://api.vapi.ai/call", headers={"Authorization": f"Bearer {key}"}, params={"limit": 3})
calls = r.json()
for c in calls:
    num = c.get("customer", {}).get("number", "")
    if num == "+13524349704":
        print("Status:", c.get("status"))
        print("Ended:", c.get("endedReason"))
        print("Time:", c.get("createdAt"))
        t = c.get("transcript", "")
        if t:
            print("Transcript:")
            print(t[:1000])
        a = c.get("analysis", {})
        if a and a.get("summary"):
            print("Summary:", a["summary"])
        break
