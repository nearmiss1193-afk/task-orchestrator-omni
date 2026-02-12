"""
Check what happened during Dan's test call.
Pull all evidence from DB + Vapi API for the last 30 minutes.
"""
import requests, os, json
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client

sb_url = os.getenv('SUPABASE_URL')
sb_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(sb_url, sb_key)

cutoff = (datetime.utcnow() - timedelta(minutes=60)).isoformat()

print("=" * 60)
print("EVIDENCE CHECK — Dan's test call")
print(f"Checking events after {cutoff}")
print("=" * 60)

# 1. vapi_debug_logs — ALL entries in last 60 min
print("\n--- vapi_debug_logs (last 60 min) ---")
try:
    logs = sb.table("vapi_debug_logs").select("*").gte("created_at", cutoff).order("created_at", desc=True).limit(20).execute()
    if logs.data:
        for i, log in enumerate(logs.data):
            print(f"\n  [{i+1}] event_type: {log.get('event_type', 'NONE')}")
            print(f"      created_at: {log.get('created_at', 'NONE')}")
            print(f"      call_direction: {log.get('call_direction', 'NONE')}")
            print(f"      normalized_phone: {log.get('normalized_phone', 'NONE')}")
            print(f"      customer_name: {log.get('customer_name_found', 'NONE')}")
            print(f"      call_mode: {log.get('call_mode', 'NONE')}")
            print(f"      notes: {log.get('notes', 'NONE')}")
    else:
        print("  ❌ NO ENTRIES — webhook may not be firing at all")
except Exception as e:
    print(f"  ERROR: {e}")

# 2. conversation_logs — voice entries in last 60 min
print("\n--- conversation_logs (voice, last 60 min) ---")
try:
    convs = sb.table("conversation_logs").select("*").eq("channel", "voice").gte("timestamp", cutoff).order("timestamp", desc=True).limit(10).execute()
    if convs.data:
        for i, c in enumerate(convs.data):
            print(f"\n  [{i+1}] timestamp: {c.get('timestamp', 'NONE')}")
            print(f"      customer_id: {c.get('customer_id', 'NONE')}")
            print(f"      direction: {c.get('direction', 'NONE')}")
            print(f"      content: {str(c.get('content', ''))[:150]}")
            print(f"      sarah_response: {str(c.get('sarah_response', ''))[:150]}")
    else:
        print("  ❌ NO VOICE ENTRIES in last 60 min")
except Exception as e:
    print(f"  ERROR: {e}")

# 3. Vapi recent calls in last 60 min
print("\n--- Vapi API: Recent calls ---")
vapi_key = os.getenv('VAPI_PRIVATE_KEY')
try:
    r = requests.get('https://api.vapi.ai/call', headers={'Authorization': f'Bearer {vapi_key}'}, params={'limit': 5}, timeout=15)
    if r.status_code == 200:
        calls = r.json()
        for i, c in enumerate(calls[:5]):
            created = c.get('createdAt', 'NONE')
            ended = c.get('endedAt', 'NONE')
            status = c.get('status', 'NONE')
            cust_num = c.get('customer', {}).get('number', 'NONE')
            phone_num = c.get('phoneNumber', {}).get('number', 'NONE')
            assistant_id = c.get('assistantId', 'NONE')[:20]
            duration = c.get('costs', [{}])[0].get('duration', '?') if c.get('costs') else '?'
            
            # Check serverMessages config
            server_msgs = c.get('serverMessages', [])
            has_eocr = 'end-of-call-report' in server_msgs if server_msgs else 'NOT SET'
            
            print(f"\n  [{i+1}] created: {created}")
            print(f"      ended: {ended}")
            print(f"      status: {status}")
            print(f"      customer: {cust_num}")
            print(f"      phone: {phone_num}")
            print(f"      assistant: {assistant_id}")
            print(f"      serverMessages: {server_msgs}")
            print(f"      has end-of-call-report: {has_eocr}")
    else:
        print(f"  ERROR: {r.status_code}")
except Exception as e:
    print(f"  ERROR: {e}")

# 4. Check assistant serverMessages config
print("\n--- Vapi Assistants: serverMessages config ---")
for aid, name in [("1a797f12-e2dd-4f7f-b2c5-08c38c74859a", "Sarah the Spartan"), 
                   ("ae717f29-6542-422f-906f-ee7ba6fa0bfe", "Sarah Spart#")]:
    try:
        r = requests.get(f'https://api.vapi.ai/assistant/{aid}', headers={'Authorization': f'Bearer {vapi_key}'}, timeout=10)
        if r.status_code == 200:
            a = r.json()
            sm = a.get('serverMessages', 'NOT SET')
            su = a.get('serverUrl', 'NONE')
            server = a.get('server', {})
            print(f"\n  {name} ({aid[:12]}...):")
            print(f"    serverUrl: {su[:60]}")
            print(f"    server.url: {server.get('url', 'NONE')[:60] if server else 'NONE'}")
            print(f"    serverMessages: {sm}")
            has_eocr = 'end-of-call-report' in sm if isinstance(sm, list) else 'NOT A LIST'
            print(f"    has end-of-call-report: {has_eocr}")
    except Exception as e:
        print(f"  ERROR for {name}: {e}")

# 5. Check phone number we care about
print("\n--- Phone +18632132505 config ---")
try:
    all_phones = requests.get('https://api.vapi.ai/phone-number', headers={'Authorization': f'Bearer {vapi_key}'}, timeout=15).json()
    for p in all_phones:
        if p.get('number') == '+18632132505':
            print(f"  serverUrl: {p.get('serverUrl', 'NONE')}")
            print(f"  assistantId: {p.get('assistantId', 'NONE')}")
            print(f"  serverMessages (phone-level): {p.get('serverMessages', 'NOT SET')}")
            break
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("EVIDENCE CHECK COMPLETE")
print("=" * 60)
