import requests
import json

# Try the Manus API to get the actual file download URL
api_url = "https://api.manus.im/api/v1/share/file/70f78484-8c09-4c82-a200-0e723e9c8980"

r = requests.get(api_url, headers={
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}, timeout=15)

print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type', '')}")

with open("manus_response.json", "w") as f:
    f.write(r.text)

print("Response saved to manus_response.json")
print(f"Response: {r.text[:2000]}")
