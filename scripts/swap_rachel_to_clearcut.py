import os, requests
from dotenv import load_dotenv
load_dotenv('.env')

VAPI_KEY = os.environ['VAPI_PRIVATE_KEY']
RACHEL_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"

script = open('scripts/rachel_clearcut_tree.txt', 'r', encoding='utf-8').read()

r = requests.patch(
    f"https://api.vapi.ai/assistant/{RACHEL_ID}",
    headers={
        "Authorization": f"Bearer {VAPI_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "name": "Rachel (Onboarding - Clear Cut Tree Masters)",
        "firstMessage": "Hey! Thanks so much for taking the time to chat with us. I'm Rachel from AI Service Company - I'm going to walk you through exactly what we can do for Clear Cut Tree Masters. This should be fun! How are you doing today?",
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [{"role": "system", "content": script}],
            "temperature": 0.7
        }
    }
)

if r.status_code == 200:
    print("SUCCESS: Rachel swapped to Clear Cut Tree Masters script")
else:
    print(f"FAILED: {r.status_code} - {r.text[:300]}")
