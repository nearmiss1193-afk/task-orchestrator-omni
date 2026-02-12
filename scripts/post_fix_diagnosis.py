"""
POST-FIX DIAGNOSIS - What's STILL broken after all 6 fixes?
Check everything fresh, then feed to board call.
"""
import requests, os, json
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(url, key)
vapi_key = os.getenv('VAPI_PRIVATE_KEY')
vh = {'Authorization': f'Bearer {vapi_key}'}

dan = "+13529368152"
dan_cid = "37610d10-7d62-436a-aa3b-eacd197b74bb"

out = []

# 1. What name does context_summary have NOW?
out.append("=" * 60)
out.append("1. CURRENT CUSTOMER MEMORY STATE")
out.append("=" * 60)
try:
    r = sb.table("customer_memory").select("*").eq("customer_id", dan_cid).single().execute()
    d = r.data
    ctx = d.get('context_summary', {})
    out.append(f"contact_name: {ctx.get('contact_name', 'NOT SET')}")
    out.append(f"questions_asked: {ctx.get('questions_asked', [])}")
    out.append(f"last_interaction: {d.get('last_interaction', 'NONE')}")
    out.append(f"full context: {json.dumps(ctx, indent=2)}")
except Exception as e:
    out.append(f"ERROR: {e}")

# 2. Recent conversation logs (any new ones since our fix at ~15:14?)
out.append("\n" + "=" * 60)
out.append("2. CONVERSATION LOGS SINCE FIX (~15:14 EST = 20:14 UTC)")
out.append("=" * 60)
try:
    logs = sb.table("conversation_logs").select("channel,direction,content,sarah_response,timestamp").eq("customer_id", dan_cid).order("timestamp", desc=True).limit(5).execute()
    for row in (logs.data or []):
        ts = row.get('timestamp','')[:19]
        ch = row.get('channel','?')
        content = (row.get('content') or '')[:120]
        sarah = (row.get('sarah_response') or '')[:120]
        out.append(f"\n  [{ts}] {ch}")
        out.append(f"    User: {content}")
        out.append(f"    Sarah: {sarah}")
    if not logs.data:
        out.append("  NO NEW LOGS - SMS handler may not be getting called")
except Exception as e:
    out.append(f"ERROR: {e}")

# 3. Vapi debug logs - any since our fix?
out.append("\n" + "=" * 60)
out.append("3. VAPI DEBUG LOGS (any new ones?)")
out.append("=" * 60)
try:
    dl = sb.table("vapi_debug_logs").select("event_type,call_direction,normalized_phone,lookup_result,customer_name_found,notes,created_at").order("created_at", desc=True).limit(5).execute()
    for row in (dl.data or []):
        ts = row.get('created_at','')[:19]
        evt = row.get('event_type','?')
        ph = row.get('normalized_phone','?')
        name = row.get('customer_name_found','?')
        notes = (row.get('notes') or '')[:100]
        out.append(f"  [{ts}] {evt} | {ph} | name: {name} | {notes}")
    if not dl.data:
        out.append("  ZERO debug logs - webhook NEVER called")
except Exception as e:
    out.append(f"ERROR: {e}")

# 4. Verify BOTH assistants' config
out.append("\n" + "=" * 60)
out.append("4. VAPI ASSISTANT CONFIGS (post-fix)")
out.append("=" * 60)
for name, aid in [("Sarah the Spartan", "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"), ("Sarah Spart#", "ae717f29-6542-422f-906f-ee7ba6fa0bfe")]:
    try:
        a = requests.get(f'https://api.vapi.ai/assistant/{aid}', headers=vh, timeout=15).json()
        out.append(f"\n  {name} ({aid[:16]})")
        out.append(f"    serverUrl: {a.get('serverUrl', 'NONE')}")
        out.append(f"    serverMessages: {a.get('serverMessages', 'NOT SET')}")
        srv = a.get('server', {})
        out.append(f"    server.url: {srv.get('url', 'NONE')}")
    except Exception as e:
        out.append(f"  {name}: ERROR {e}")

# 5. Recent VAPI calls - which assistant do they use NOW?
out.append("\n" + "=" * 60)
out.append("5. MOST RECENT VAPI CALLS (after fix)")
out.append("=" * 60)
try:
    calls = requests.get('https://api.vapi.ai/call?limit=5', headers=vh, timeout=15).json()
    for c in calls[:5]:
        out.append(f"\n  Call: {c['id'][:24]}")
        out.append(f"  Created: {c.get('createdAt','')[:19]}")
        out.append(f"  Status: {c.get('status')} | Reason: {c.get('endedReason','?')}")
        out.append(f"  Customer: {c.get('customer',{}).get('number','?')}")
        out.append(f"  AssistantId: {c.get('assistantId','?')}")
        # Check messages from the call
        msgs = c.get('messages', [])
        if msgs:
            out.append(f"  Messages: {len(msgs)} entries")
except Exception as e:
    out.append(f"ERROR: {e}")

# 6. Check phone numbers pointing to which assistant
out.append("\n" + "=" * 60)
out.append("6. PHONE NUMBER CONFIGS")
out.append("=" * 60)
known_phones = [
    ("86f73243-8916-4897-bd91-c066193c22b7", "Sarah Spart# phone"),
]
for pid, label in known_phones:
    try:
        p = requests.get(f'https://api.vapi.ai/phone-number/{pid}', headers=vh, timeout=15).json()
        out.append(f"\n  {label} ({p.get('number','')})")
        out.append(f"    assistantId: {p.get('assistantId', 'NONE')}")
        out.append(f"    serverUrl: {p.get('serverUrl', 'NONE')}")
    except Exception as e:
        out.append(f"  {label}: ERROR {e}")

# List ALL phone numbers
try:
    all_phones = requests.get('https://api.vapi.ai/phone-number', headers=vh, timeout=15).json()
    out.append(f"\n  ALL PHONE NUMBERS ({len(all_phones)} total):")
    for p in all_phones:
        out.append(f"    {p.get('number','')} -> assistant: {p.get('assistantId','NONE')[:20]} | serverUrl: {p.get('serverUrl','NONE')[:60]}")
except Exception as e:
    out.append(f"  All phones ERROR: {e}")

# 7. What number does Dan actually call?
out.append("\n" + "=" * 60)
out.append("7. WHICH NUMBER RECEIVES THE CALLS?")
out.append("=" * 60)
try:
    calls = requests.get('https://api.vapi.ai/call?limit=3', headers=vh, timeout=15).json()
    for c in calls[:3]:
        phone_num = c.get('phoneNumber', {})
        out.append(f"\n  Call {c['id'][:16]}")
        out.append(f"    phoneNumber.id: {phone_num.get('id', 'N/A')}")
        out.append(f"    phoneNumber.number: {phone_num.get('number', 'N/A')}")
        out.append(f"    phoneNumber.assistantId: {phone_num.get('assistantId', 'N/A')}")
        out.append(f"    phoneNumber.serverUrl: {phone_num.get('serverUrl', 'N/A')}")
        out.append(f"    call assistantId: {c.get('assistantId', 'N/A')}")
except Exception as e:
    out.append(f"ERROR: {e}")

result = "\n".join(out)
with open('scripts/post_fix_diagnosis.txt', 'w', encoding='utf-8') as f:
    f.write(result)
print("Done - saved to scripts/post_fix_diagnosis.txt")
