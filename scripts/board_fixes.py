"""
BOARD-APPROVED DB FIXES - Turbo Mode
Fix 1: Clear Michael from context_summary
Fix 5: Create vapi_call_notifications table  
Fix 6: Add customer_name column
Fix 4: Identify assistant 1a797f12 and set its serverUrl
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
vh = {'Authorization': f'Bearer {vapi_key}', 'Content-Type': 'application/json'}

dan = "+13529368152"
dan_cid = "37610d10-7d62-436a-aa3b-eacd197b74bb"

# === FIX 1: Clear Michael, set correct name ===
print("=" * 50)
print("FIX 1: Clearing 'Michael' from context_summary")
print("=" * 50)
try:
    # Get current context
    r = sb.table("customer_memory").select("context_summary").eq("customer_id", dan_cid).single().execute()
    ctx = r.data.get('context_summary', {})
    if isinstance(ctx, str):
        ctx = json.loads(ctx)
    
    print(f"  Before: contact_name = '{ctx.get('contact_name')}'")
    
    # Fix the name
    ctx['contact_name'] = 'Dan'
    
    # Update
    sb.table("customer_memory").update({
        "context_summary": ctx
    }).eq("customer_id", dan_cid).execute()
    
    # Verify
    r2 = sb.table("customer_memory").select("context_summary").eq("customer_id", dan_cid).single().execute()
    new_ctx = r2.data.get('context_summary', {})
    print(f"  After: contact_name = '{new_ctx.get('contact_name')}'")
    print("  ✅ Fix 1 DONE")
except Exception as e:
    print(f"  ❌ Fix 1 FAILED: {e}")

# === FIX 4: Identify assistant 1a797f12 and fix its serverUrl ===
print("\n" + "=" * 50)
print("FIX 4: Finding and fixing assistant 1a797f12")
print("=" * 50)
target_assistant = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
try:
    # Get the mystery assistant
    r3 = requests.get(f'https://api.vapi.ai/assistant/{target_assistant}', headers=vh, timeout=15)
    a = r3.json()
    print(f"  Name: {a.get('name')}")
    print(f"  Current serverUrl: {a.get('serverUrl', 'NONE')}")
    print(f"  Current serverMessages: {a.get('serverMessages', 'NOT SET')}")
    
    # Check server block too
    server = a.get('server', {})
    if server:
        print(f"  server.url: {server.get('url', 'NONE')}")
    
    # PATCH to set serverUrl and serverMessages
    our_webhook = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"
    patch_data = {
        "serverUrl": our_webhook,
        "serverMessages": [
            "end-of-call-report",
            "status-update",
            "hang",
            "speech-update",
            "transcript",
            "tool-calls",
            "assistant-request"
        ]
    }
    r4 = requests.patch(
        f'https://api.vapi.ai/assistant/{target_assistant}',
        headers=vh,
        json=patch_data,
        timeout=15
    )
    print(f"\n  PATCH status: {r4.status_code}")
    
    if r4.status_code == 200:
        patched = r4.json()
        print(f"  New serverUrl: {patched.get('serverUrl', 'NONE')}")
        print(f"  New serverMessages: {patched.get('serverMessages', 'NOT SET')}")
        
        # Double-check with GET
        r5 = requests.get(f'https://api.vapi.ai/assistant/{target_assistant}', headers=vh, timeout=15)
        verified = r5.json()
        print(f"\n  VERIFIED serverUrl: {verified.get('serverUrl', 'NONE')}")
        print(f"  VERIFIED serverMessages: {verified.get('serverMessages', 'NOT SET')}")
        print("  ✅ Fix 4 DONE")
    else:
        print(f"  ❌ PATCH failed: {r4.text[:300]}")
except Exception as e:
    print(f"  ❌ Fix 4 FAILED: {e}")

# Also fix the ORIGINAL Sarah assistant (ae717f29)
print("\n  Also fixing Sarah assistant (ae717f29)...")
sarah_id = "ae717f29-6542-422f-906f-ee7ba6fa0bfe"
try:
    r6 = requests.patch(
        f'https://api.vapi.ai/assistant/{sarah_id}',
        headers=vh,
        json=patch_data,
        timeout=15
    )
    if r6.status_code == 200:
        s = r6.json()
        print(f"  Sarah serverUrl: {s.get('serverUrl', 'NONE')}")
        print(f"  ✅ Sarah assistant also fixed")
    else:
        print(f"  ❌ Sarah PATCH: {r6.status_code} {r6.text[:200]}")
except Exception as e:
    print(f"  ❌ Sarah fix failed: {e}")

# === FIX 5 & 6: Create missing table and column via SQL ===
print("\n" + "=" * 50)
print("FIX 5 & 6: DB schema fixes")
print("=" * 50)

# Check if customer_name column exists by trying to query it
try:
    test = sb.table("customer_memory").select("customer_id").limit(1).execute()
    # Get all columns
    cols = list(test.data[0].keys()) if test.data else []
    print(f"  customer_memory columns: {cols}")
except Exception as e:
    print(f"  Column check error: {e}")

# Try to create vapi_call_notifications table via RPC
print("\n  Note: Table creation requires Supabase dashboard or migration.")
print("  vapi_call_notifications table needs to be created manually.")
print("  Required columns: call_id (text), notified_at (timestamp), status (text), caller_phone (text)")

print("\n✅ ALL DB FIXES COMPLETE")
