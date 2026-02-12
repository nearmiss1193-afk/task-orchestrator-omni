"""
FULL BOARD DIAGNOSIS - RESEARCH ONLY
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

out = []
dan = "+13529368152"
SARAH_ID = "ae717f29-6542-422f-906f-ee7ba6fa0bfe"
SARAH_PHONE = "86f73243-8916-4897-bd91-c066193c22b7"

# 1. Verify Vapi config
out.append("=" * 60)
out.append("1. VAPI SARAH ASSISTANT CONFIG")
out.append("=" * 60)
try:
    a = requests.get(f'https://api.vapi.ai/assistant/{SARAH_ID}', headers=vh, timeout=15).json()
    out.append(f"Name: {a.get('name')}")
    out.append(f"serverUrl: {a.get('serverUrl', 'NONE')}")
    out.append(f"serverMessages: {a.get('serverMessages', 'NOT SET')}")
    s = a.get('server', {})
    if s:
        out.append(f"server.url: {s.get('url', 'N/A')}")
    
    p = requests.get(f'https://api.vapi.ai/phone-number/{SARAH_PHONE}', headers=vh, timeout=15).json()
    out.append(f"\nPhone: {p.get('number')}")
    out.append(f"Phone serverUrl: {p.get('serverUrl', 'NONE')}")
    out.append(f"Phone assistantId: {p.get('assistantId', 'NONE')}")
except Exception as e:
    out.append(f"ERROR: {e}")

# 2. Recent calls
out.append("\n" + "=" * 60)
out.append("2. RECENT VAPI CALLS (last 10)")
out.append("=" * 60)
try:
    calls = requests.get('https://api.vapi.ai/call?limit=10', headers=vh, timeout=15).json()
    for c in calls:
        out.append(f"\n  Call: {c['id'][:24]}")
        out.append(f"  Status: {c.get('status')} | Customer: {c.get('customer',{}).get('number','?')}")
        out.append(f"  Created: {c.get('createdAt','')[:19]} | Ended: {(c.get('endedAt') or 'ACTIVE')[:19]}")
        out.append(f"  Reason: {c.get('endedReason','?')}")
        out.append(f"  Assistant: {c.get('assistantId','?')[:20]}")
        # Check if assistant has serverUrl in the call context
        ca = c.get('assistant', {})
        if ca:
            out.append(f"  Call-level serverUrl: {ca.get('serverUrl', 'NONE')}")
            out.append(f"  Call-level serverMessages: {ca.get('serverMessages', 'NOT SET')}")
except Exception as e:
    out.append(f"ERROR: {e}")

# 3. Where is Michael?
out.append("\n" + "=" * 60)
out.append("3. WHERE IS 'MICHAEL' STORED?")
out.append("=" * 60)
try:
    r = sb.table("customer_memory").select("*").eq("phone_number", dan).execute()
    if r.data:
        row = r.data[0]
        out.append(f"customer_id: {row.get('customer_id')}")
        out.append(f"customer_name field: '{row.get('customer_name')}'")
        out.append(f"phone: {row.get('phone_number')}")
        out.append(f"status: {row.get('status')}")
        out.append(f"updated_at: {row.get('updated_at')}")
        out.append(f"last_interaction: {row.get('last_interaction')}")
        ctx = row.get('context_summary', {})
        if isinstance(ctx, str):
            try:
                ctx = json.loads(ctx)
            except:
                pass
        out.append(f"context_summary:")
        out.append(json.dumps(ctx, indent=4))
        
        # Check specifically where Michael appears
        out.append(f"\nMICHAEL APPEARS IN:")
        if 'michael' in str(row.get('customer_name','')).lower():
            out.append(f"  -> customer_name field: '{row.get('customer_name')}'")
        if 'michael' in json.dumps(ctx).lower():
            out.append(f"  -> context_summary.contact_name: '{ctx.get('contact_name','')}'")
        if 'michael' in str(row.get('context_summary',{})).lower():
            out.append(f"  -> raw context_summary contains 'Michael'")
    else:
        out.append("NO customer_memory record for Dan!")
except Exception as e:
    out.append(f"ERROR: {e}")

# Check ALL records
out.append("\nAll customer_memory records:")
try:
    all_cm = sb.table("customer_memory").select("customer_id,phone_number,customer_name").execute()
    for row in (all_cm.data or []):
        out.append(f"  {row.get('phone_number')} | name: {row.get('customer_name')} | id: {str(row.get('customer_id',''))[:16]}")
except Exception as e:
    out.append(f"ERROR: {e}")

# 4. Conversation logs
out.append("\n" + "=" * 60)
out.append("4. CONVERSATION LOGS")
out.append("=" * 60)
dan_cid = None
try:
    r2 = sb.table("customer_memory").select("customer_id").eq("phone_number", dan).execute()
    if r2.data:
        dan_cid = r2.data[0]['customer_id']
        out.append(f"Dan's customer_id: {dan_cid}")
except:
    pass

if dan_cid:
    try:
        logs = sb.table("conversation_logs").select("channel,direction,content,sarah_response,timestamp").eq("customer_id", dan_cid).order("timestamp", desc=True).limit(15).execute()
        if logs.data:
            out.append(f"Found {len(logs.data)} conversation logs:")
            for row in logs.data:
                ts = row.get('timestamp','')[:19]
                ch = row.get('channel','?')
                d = row.get('direction','?')
                c = (row.get('content') or '')[:120]
                sr = (row.get('sarah_response') or '')[:120]
                out.append(f"\n  [{ts}] {ch}/{d}")
                out.append(f"    User: {c}")
                out.append(f"    Sarah: {sr}")
        else:
            out.append("ZERO conversation logs for Dan!")
    except Exception as e:
        out.append(f"ERROR reading logs: {e}")
else:
    out.append("Could not find Dan's customer_id")

# 5. Vapi debug logs 
out.append("\n" + "=" * 60)
out.append("5. VAPI DEBUG LOGS (recent)")
out.append("=" * 60)
try:
    dl = sb.table("vapi_debug_logs").select("event_type,call_direction,normalized_phone,lookup_result,customer_name_found,notes,created_at").order("created_at", desc=True).limit(10).execute()
    if dl.data:
        for row in dl.data:
            ts = row.get('created_at','')[:19]
            evt = row.get('event_type','?')
            d = row.get('call_direction','?')
            ph = row.get('normalized_phone','?')
            lookup = row.get('lookup_result','?')
            name = row.get('customer_name_found','?')
            notes = (row.get('notes') or '')[:150]
            out.append(f"\n  [{ts}] {evt} | {d} | {ph}")
            out.append(f"    lookup: {lookup} | name: {name}")
            if notes:
                out.append(f"    notes: {notes}")
    else:
        out.append("NO debug logs at all")
except Exception as e:
    out.append(f"ERROR: {e}")

# 6. Notification table
out.append("\n" + "=" * 60)
out.append("6. CALL NOTIFICATION RECORDS")
out.append("=" * 60)
try:
    nl = sb.table("vapi_call_notifications").select("*").order("notified_at", desc=True).limit(5).execute()
    if nl.data:
        for row in nl.data:
            out.append(f"  call_id: {row.get('call_id','')[:24]} | notified: {row.get('notified_at','')[:19]} | status: {row.get('status','?')}")
    else:
        out.append("EMPTY - Zero notification records ever")
except Exception as e:
    out.append(f"Table error: {e}")

result = "\n".join(out)
with open('scripts/full_diagnosis.txt', 'w', encoding='utf-8') as f:
    f.write(result)
print("Done - saved to scripts/full_diagnosis.txt")
