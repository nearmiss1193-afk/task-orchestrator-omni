"""Full customer memory check"""
from dotenv import load_dotenv
import os
import json
load_dotenv()

from supabase import create_client

sb = create_client(os.getenv('NEXT_PUBLIC_SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

# Check all customer_memory entries
r = sb.table('customer_memory').select('*').execute()
print(f"=== CUSTOMER_MEMORY ({len(r.data)} entries) ===")
for row in r.data:
    print(f"\nPhone: {row.get('phone_number')}")
    print(f"  Status: {row.get('status')}")
    print(f"  Context: {json.dumps(row.get('context_summary'), indent=4) if row.get('context_summary') else 'None'}")
    print(f"  Created: {row.get('created_at')}")
    print(f"  Updated: {row.get('updated_at')}")

# Check if vapi_debug_logs table exists by getting count
print("\n=== VAPI_DEBUG_LOGS ===")
try:
    r2 = sb.table('vapi_debug_logs').select('*', count='exact').limit(0).execute()
    print(f"Table exists, {r2.count} rows")
except Exception as e:
    print(f"Table error: {e}")
