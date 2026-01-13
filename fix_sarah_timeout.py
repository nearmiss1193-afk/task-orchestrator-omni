"""
Fix Sarah - Add first message and increase silence timeout
"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

print("="*60)
print("FIXING SARAH - Silence Timeout + First Message")
print("="*60)

# Fix Sarah's settings
update_data = {
    "firstMessage": "Hey thanks for calling AI Service Co! This is Sarah, how can I help you today?",
    "silenceTimeoutSeconds": 30,  # Increase from 10 to 30
    "responseDelaySeconds": 0.3,
    "endCallMessage": "Awesome, thanks so much for calling! Have a great day!"
}

print(f"\nUpdating Sarah with:")
for k, v in update_data.items():
    print(f"  {k}: {v}")

r = requests.patch(
    f"https://api.vapi.ai/assistant/{SARAH_ID}",
    headers=headers,
    json=update_data
)

if r.ok:
    print("\n SUCCESS! Sarah updated")
    data = r.json()
    print(f"  New firstMessage: {data.get('firstMessage','?')[:50]}...")
    print(f"  New silenceTimeoutSeconds: {data.get('silenceTimeoutSeconds')}")
else:
    print(f"\n ERROR: {r.status_code}")
    print(r.text[:500])

print("\n" + "="*60)
print("Try calling again - Sarah should greet you now!")
print("="*60)
