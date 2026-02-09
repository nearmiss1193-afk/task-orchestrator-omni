"""Full database diagnostic for voice memory investigation"""
from dotenv import load_dotenv
import os
import json
load_dotenv()

from supabase import create_client

sb = create_client(os.getenv('NEXT_PUBLIC_SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

print("=" * 60)
print("VOICE MEMORY INVESTIGATION - DATABASE EVIDENCE")
print("=" * 60)

# 1. Customer Memory
print("\n=== CUSTOMER_MEMORY TABLE ===")
try:
    r = sb.table('customer_memory').select('*').execute()
    print(f"Total entries: {len(r.data)}")
    for row in r.data:
        print(f"\n  Phone: {row.get('phone_number')}")
        print(f"  Status: {row.get('status')}")
        ctx = row.get('context_summary', {})
        if ctx:
            print(f"  Contact Name: {ctx.get('contact_name', 'NOT STORED')}")
            print(f"  Business Type: {ctx.get('business_type', 'NOT STORED')}")
            print(f"  Last Channel: {ctx.get('last_channel', 'NOT STORED')}")
        print(f"  Created: {row.get('created_at')}")
        print(f"  Updated: {row.get('updated_at')}")
except Exception as e:
    print(f"ERROR: {e}")

# 2. Conversation Logs
print("\n=== CONVERSATION_LOGS TABLE (last 10) ===")
try:
    r = sb.table('conversation_logs').select('*').order('created_at', desc=True).limit(10).execute()
    print(f"Total found: {len(r.data)}")
    for row in r.data:
        print(f"\n  Phone: {row.get('phone_number', row.get('customer_phone', 'N/A'))}")
        print(f"  Channel: {row.get('channel', 'N/A')}")
        print(f"  Direction: {row.get('direction', 'N/A')}")
        print(f"  Created: {row.get('created_at')}")
        msg = row.get('message_content', row.get('user_message', ''))
        if msg:
            print(f"  Message: {msg[:100]}...")
except Exception as e:
    print(f"ERROR: {e}")

# 3. Vapi Debug Logs
print("\n=== VAPI_DEBUG_LOGS TABLE ===")
try:
    r = sb.table('vapi_debug_logs').select('*').order('created_at', desc=True).limit(5).execute()
    print(f"Total entries: {len(r.data)}")
    if len(r.data) == 0:
        print("  ⚠️ NO DEBUG LOGS - Voice calls not generating debug data")
    for row in r.data:
        print(f"\n  Event: {row.get('event_type')}")
        print(f"  Phone: {row.get('phone_number')}")
        print(f"  Created: {row.get('created_at')}")
except Exception as e:
    print(f"ERROR: {e}")

# 4. Check for any recent voice webhook activity
print("\n=== SEARCHING FOR DAN'S PHONE NUMBER ===")
dan_phones = ['+13529368152', '3529368152', '+1352-936-8152']
for phone in dan_phones:
    try:
        r = sb.table('customer_memory').select('*').eq('phone_number', phone).execute()
        if r.data:
            print(f"  FOUND: {phone}")
            print(f"  Data: {json.dumps(r.data[0], indent=4)}")
        else:
            print(f"  NOT FOUND: {phone}")
    except:
        pass

print("\n" + "=" * 60)
print("END OF DATABASE EVIDENCE")
print("=" * 60)
