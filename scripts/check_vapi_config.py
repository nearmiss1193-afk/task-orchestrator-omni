"""Check Vapi config and save results to file"""
import requests, os, json
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}'}
out = []

# Assistants
r = requests.get('https://api.vapi.ai/assistant', headers=headers, timeout=15)
out.append("=== ASSISTANTS ===")
for a in r.json()[:3]:
    out.append(f"Name: {a.get('name','?')}")
    out.append(f"ID: {a['id']}")
    out.append(f"serverUrl: {a.get('serverUrl','NONE')}")
    out.append(f"serverMessages: {json.dumps(a.get('serverMessages','NOT_SET'))}")
    s = a.get('server',{})
    if s:
        out.append(f"server.url: {s.get('url','N/A')}")
    out.append("")

# Phone numbers
r2 = requests.get('https://api.vapi.ai/phone-number', headers=headers, timeout=15)
out.append("=== PHONE NUMBERS ===")
for p in r2.json()[:5]:
    out.append(f"Number: {p.get('number','?')}")
    out.append(f"ID: {p['id']}")
    out.append(f"serverUrl: {p.get('serverUrl','NONE')}")
    out.append(f"assistantId: {p.get('assistantId','NONE')}")
    out.append("")

# Recent calls
r3 = requests.get('https://api.vapi.ai/call?limit=5', headers=headers, timeout=15)
out.append("=== RECENT CALLS ===")
for c in r3.json()[:5]:
    out.append(f"ID: {c['id'][:20]}")
    out.append(f"status: {c.get('status')} | customer: {c.get('customer',{}).get('number','?')}")
    out.append(f"created: {c.get('createdAt','')[:19]} | ended: {(c.get('endedAt') or 'active')[:19]}")
    out.append(f"reason: {c.get('endedReason','?')} | msgs: {len(c.get('messages',[]) or [])}")
    out.append("")

# Test notification
out.append("=== NOTIFICATION TEST ===")
dan_phone = "+13529368152"
ghl_webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
msg = "ANTIGRAVITY TURBO: Notification test. If you see this, the pipeline works."
try:
    r4 = requests.post(ghl_webhook, json={"phone": dan_phone, "message": msg}, timeout=10)
    out.append(f"Response: {r4.status_code} | {r4.text[:200]}")
except Exception as e:
    out.append(f"FAILED: {e}")

result = "\n".join(out)
with open('scripts/vapi_result.txt', 'w', encoding='utf-8') as f:
    f.write(result)
print(result)
