import os, json, requests
from dotenv import load_dotenv
load_dotenv('.env')

key = os.environ['VAPI_PRIVATE_KEY']
r = requests.get(f"https://api.vapi.ai/assistant/033ec1d3-e17d-4611-a497-b47cab1fdb4e", 
                 headers={"Authorization": f"Bearer {key}"})
data = r.json()

with open('scripts/rachel_verify.md', 'w', encoding='utf-8') as f:
    f.write(f"Name: {data.get('name')}\n")
    f.write(f"Model: {data.get('model', {}).get('model')}\n")
    f.write(f"First Message: {data.get('firstMessage', 'NONE')[:100]}\n")
    msgs = data.get('model', {}).get('messages', [])
    if msgs:
        f.write(f"System Prompt Preview: {msgs[0].get('content', '')[:200]}\n")
    else:
        f.write("System Prompt: NONE\n")

print(f"Name: {data.get('name')}")
print(f"Model: {data.get('model', {}).get('model')}")
print(f"First message starts with: {data.get('firstMessage', 'NONE')[:60]}")
