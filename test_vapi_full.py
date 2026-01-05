
import os
import requests
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")

print("=== VAPI FULL DIAGNOSTIC ===")
print(f"Key: {VAPI_KEY[:10]}...")

url = "https://api.vapi.ai/phone-number"
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

print("\n[1] Phone Numbers:")
res = requests.get(url, headers=headers)
if res.status_code == 200:
    nums = res.json()
    print(f"   Found: {len(nums)}")
    for n in nums:
        print(f"   ---")
        print(f"   ID: {n.get('id')}")
        print(f"   Number: {n.get('number')}")
        print(f"   Provider: {n.get('provider')}")
        print(f"   Name: {n.get('name')}")
else:
    print(f"   Error: {res.status_code} - {res.text}")

print("\n[2] Assistants:")
url2 = "https://api.vapi.ai/assistant"
res2 = requests.get(url2, headers=headers)
if res2.status_code == 200:
    assts = res2.json()
    print(f"   Found: {len(assts)}")
    for a in assts[:3]:  # First 3 only
        print(f"   ---")
        print(f"   ID: {a.get('id')}")
        print(f"   Name: {a.get('name')}")
else:
    print(f"   Error: {res2.status_code} - {res2.text}")

print("\n=== DONE ===")
