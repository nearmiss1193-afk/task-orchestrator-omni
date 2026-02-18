import os, json, requests
from dotenv import load_dotenv
load_dotenv('.env')

key = os.environ['VAPI_PRIVATE_KEY']
r = requests.get('https://api.vapi.ai/phone-number', headers={'Authorization': f'Bearer {key}'})
data = r.json()

out = []
for p in data:
    num = p.get('number', '?')
    pid = p['id']
    name = p.get('name', 'unnamed')
    asst = p.get('assistantId', 'NONE')
    out.append(f"{num} | {pid} | name={name} | assistantId={asst}")

with open('scripts/vapi_phones.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
print(f"Found {len(data)} phone numbers")
