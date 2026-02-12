"""Fix Vapi assistants with VALID serverMessages + fix server.url"""
import requests, os, json
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

vapi_key = os.getenv('VAPI_PRIVATE_KEY')
vh = {'Authorization': f'Bearer {vapi_key}', 'Content-Type': 'application/json'}
our_webhook = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"

# Valid serverMessages from the Vapi error
valid_messages = [
    "end-of-call-report",
    "status-update",
    "hang",
    "speech-update",
    "transcript",
    "function-call",
    "assistant.started",
    "conversation-update"
]

assistants = {
    "Sarah the Spartan (1a797f12)": "1a797f12-e2dd-4f7f-b2c5-08c38c74859a",
    "Sarah Spart# (ae717f29)": "ae717f29-6542-422f-906f-ee7ba6fa0bfe"
}

for name, aid in assistants.items():
    print(f"\n{'='*50}")
    print(f"Patching: {name}")
    print(f"{'='*50}")
    
    patch = {
        "serverUrl": our_webhook,
        "serverMessages": valid_messages,
        "server": {
            "url": our_webhook,
            "timeoutSeconds": 30
        }
    }
    
    r = requests.patch(f'https://api.vapi.ai/assistant/{aid}', headers=vh, json=patch, timeout=15)
    print(f"PATCH status: {r.status_code}")
    
    if r.status_code == 200:
        d = r.json()
        print(f"  serverUrl: {d.get('serverUrl', 'NONE')}")
        print(f"  serverMessages: {d.get('serverMessages', 'NOT SET')}")
        srv = d.get('server', {})
        print(f"  server.url: {srv.get('url', 'NONE')}")
        
        # Verify with GET
        v = requests.get(f'https://api.vapi.ai/assistant/{aid}', headers=vh, timeout=15).json()
        print(f"\n  VERIFIED serverUrl: {v.get('serverUrl', 'NONE')}")
        print(f"  VERIFIED server.url: {v.get('server',{}).get('url', 'NONE')}")
        print(f"  ✅ DONE")
    else:
        print(f"  ❌ FAILED: {r.text[:400]}")
