"""Diagnose Sarah's memory - check all tables for Dan's phone"""
import os, json
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')
from supabase import create_client

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
sb = create_client(url, key)

dan = "+13529368152"

print("=== 1. CUSTOMER_MEMORY ===")
try:
    r = sb.table("customer_memory").select("*").eq("phone_number", dan).execute()
    if r.data:
        for row in r.data:
            print(f"  customer_id: {row.get('customer_id')}")
            print(f"  phone: {row.get('phone_number')}")
            print(f"  name: {row.get('customer_name')}")
            print(f"  status: {row.get('status')}")
            print(f"  updated_at: {row.get('updated_at')}")
            ctx = row.get('context_summary', {})
            if isinstance(ctx, str):
                try: ctx = json.loads(ctx)
                except: pass
            print(f"  context_summary: {json.dumps(ctx, indent=2)[:500]}")
    else:
        print("  NO RECORDS for Dan's phone!")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n=== 2. CONVERSATION_LOGS (last 10) ===")
try:
    r2 = sb.table("conversation_logs").select("*").eq("phone_number", dan).order("created_at", desc=True).limit(10).execute()
    if r2.data:
        for row in r2.data:
            ch = row.get('channel', '?')
            dir = row.get('direction', '?')
            msg = (row.get('message') or '')[:80]
            resp = (row.get('response') or '')[:80]
            ts = row.get('created_at', '')[:19]
            print(f"  [{ts}] {ch}/{dir}: {msg}")
            if resp:
                print(f"    -> {resp}")
    else:
        print("  NO CONVERSATION LOGS for Dan!")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n=== 3. VAPI_DEBUG_LOGS (last 5) ===")
try:
    r3 = sb.table("vapi_debug_logs").select("*").eq("normalized_phone", dan).order("created_at", desc=True).limit(5).execute()
    if r3.data:
        for row in r3.data:
            evt = row.get('event_type', '?')
            dir = row.get('call_direction', '?')
            lookup = row.get('lookup_result', '?')
            name = row.get('customer_name_found', '?')
            ts = row.get('created_at', '')[:19]
            notes = (row.get('notes') or '')[:100]
            print(f"  [{ts}] {evt} | {dir} | lookup: {lookup} | name: {name}")
            if notes:
                print(f"    notes: {notes}")
    else:
        print("  NO DEBUG LOGS for Dan!")
except Exception as e:
    print(f"  ERROR: {e}")

# Also check with different phone formats
print("\n=== 4. CHECK ALL PHONE FORMATS ===")
for fmt in [dan, "3529368152", "(352) 936-8152", "352-936-8152", "13529368152"]:
    try:
        r4 = sb.table("customer_memory").select("customer_id,phone_number").eq("phone_number", fmt).execute()
        if r4.data:
            print(f"  FOUND: '{fmt}' -> {r4.data[0].get('customer_id')}")
    except:
        pass

# Check total records
print("\n=== 5. TABLE SIZES ===")
try:
    r5 = sb.table("customer_memory").select("customer_id", count="exact").execute()
    print(f"  customer_memory: {r5.count} rows")
except Exception as e:
    print(f"  customer_memory: ERROR {e}")

try:
    r6 = sb.table("conversation_logs").select("id", count="exact").execute()
    print(f"  conversation_logs: {r6.count} rows")
except Exception as e:
    print(f"  conversation_logs: ERROR {e}")
