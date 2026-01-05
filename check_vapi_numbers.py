
import os
import requests
try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

VAPI_KEY = os.environ.get("VAPI_PRIVATE_KEY")

print(f"--- VAPI PHONE CHECK ---")
print(f"Key: {VAPI_KEY[:5]}...")

url = "https://api.vapi.ai/phone-number"
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

try:
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        nums = res.json()
        print(f"Found {len(nums)} numbers:")
        for n in nums:
            print(f" - ID: {n.get('id')} | Number: {n.get('number')}")
    else:
        print(f"Error: {res.status_code} - {res.text}")
except Exception as e:
    print(f"Ex: {e}")
