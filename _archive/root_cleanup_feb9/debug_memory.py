"""Check vapi_debug_logs to see what's actually being sent"""
from supabase import create_client

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=== VAPI DEBUG LOGS (Last 10) ===")
try:
    res = sb.table("vapi_debug_logs").select("*").order("created_at", desc=True).limit(10).execute()
    print(f"Found {len(res.data)} records")
    for i, r in enumerate(res.data):
        print(f"\n--- Log {i+1} ---")
        print(f"  Event: {r.get('event_type')}")
        print(f"  Direction: {r.get('call_direction')}")
        print(f"  Raw phone: {r.get('raw_phone')}")
        print(f"  Normalized: {r.get('normalized_phone')}")
        print(f"  Lookup: {r.get('lookup_result')}")
        print(f"  Customer name found: '{r.get('customer_name_found')}'")
        print(f"  Context summary: {str(r.get('context_summary'))[:100]}")
        overrides = r.get('assistant_overrides_sent')
        if overrides:
            print(f"  Overrides customerName: '{overrides.get('variableValues', {}).get('customerName', 'N/A')}'")
        print(f"  Created: {r.get('created_at')}")
except Exception as e:
    print(f"Error: {e}")
    # Maybe table doesn't exist - let me check
    print("\nChecking if table exists...")
    try:
        res = sb.table("vapi_debug_logs").select("*").limit(1).execute()
        print(f"Table exists, {len(res.data)} records")
    except Exception as e2:
        print(f"Table check failed: {e2}")
