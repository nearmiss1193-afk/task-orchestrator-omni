"""Check Dan's LATEST call — what did the NEW code do?"""
import requests, os, json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client

sb_url = os.getenv('SUPABASE_URL')
sb_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(sb_url, sb_key)
vapi_key = os.getenv('VAPI_PRIVATE_KEY')

print("=" * 60)
print("LATEST CALL EVIDENCE — What happened?")
print(f"Current time: {datetime.now(timezone.utc).isoformat()}")
print("=" * 60)

# 1. Latest Vapi call
print("\n--- LATEST VAPI CALLS (last 3) ---")
r = requests.get('https://api.vapi.ai/call', headers={'Authorization': f'Bearer {vapi_key}'}, params={'limit': 3}, timeout=15)
calls = r.json()
for i, c in enumerate(calls):
    print(f"\n  [{i+1}]")
    print(f"    created: {c.get('createdAt')}")
    print(f"    ended: {c.get('endedAt')}")
    print(f"    status: {c.get('status')}")
    print(f"    customer: {c.get('customer', {}).get('number')}")
    print(f"    assistant: {c.get('assistantId', '')[:20]}")
    print(f"    endedReason: {c.get('endedReason', 'NONE')}")
    
    # Check if transcript/summary exist
    transcript = c.get('transcript', '')
    summary = c.get('summary', '') or c.get('analysis', {}).get('summary', '')
    print(f"    transcript length: {len(transcript) if transcript else 0}")
    print(f"    summary: {str(summary)[:150] if summary else 'NONE'}")
    
    # Check serverUrl used for THIS specific call
    print(f"    serverUrl (call-level): {c.get('serverUrl', 'NOT SET')}")
    print(f"    server (call-level): {c.get('server', 'NOT SET')}")

# 2. Latest vapi_debug_logs (any at all?)
print("\n--- vapi_debug_logs (last 5 entries, any time) ---")
try:
    logs = sb.table("vapi_debug_logs").select("*").order("created_at", desc=True).limit(5).execute()
    if logs.data:
        for i, log in enumerate(logs.data):
            print(f"\n  [{i+1}]")
            print(f"    created: {log.get('created_at')}")
            print(f"    event_type: {log.get('event_type')}")
            print(f"    phone: {log.get('normalized_phone')}")
            print(f"    notes: {log.get('notes')}")
    else:
        print("  ❌ TABLE IS COMPLETELY EMPTY — assistant-request handler NEVER fires")
except Exception as e:
    print(f"  ERROR: {e}")

# 3. Latest conversation_logs - voice
print("\n--- conversation_logs (voice, last 5) ---")
try:
    convs = sb.table("conversation_logs").select("*").eq("channel", "voice").order("timestamp", desc=True).limit(5).execute()
    if convs.data:
        for i, c in enumerate(convs.data):
            print(f"\n  [{i+1}]")
            print(f"    timestamp: {c.get('timestamp')}")
            print(f"    direction: {c.get('direction')}")
            print(f"    content: {str(c.get('content', ''))[:100]}")
            print(f"    sarah_response: {str(c.get('sarah_response', ''))[:100]}")
    else:
        print("  ❌ NO VOICE ENTRIES AT ALL")
except Exception as e:
    print(f"  ERROR: {e}")

# 4. Latest customer_memory for Dan
print("\n--- customer_memory for Dan (+13529368152) ---")
try:
    mem = sb.table("customer_memory").select("*").eq("phone_number", "+13529368152").limit(1).execute()
    if mem.data:
        d = mem.data[0]
        print(f"  updated_at: {d.get('updated_at')}")
        ctx = d.get('context_summary', {})
        print(f"  contact_name: {ctx.get('contact_name', 'NONE')}")
        history = ctx.get('history', '')
        # Show last 500 chars of history
        print(f"  history (last 500): {history[-500:] if history else 'NONE'}")
    else:
        print("  ❌ NO RECORD FOR DAN")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("EVIDENCE COMPLETE")
