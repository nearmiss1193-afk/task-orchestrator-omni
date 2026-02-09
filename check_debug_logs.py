"""Check vapi_debug_logs to see actual webhook events"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Missing Supabase credentials")
    exit(1)

sb = create_client(url, key)

print("=== VAPI DEBUG LOGS (Last 20) ===")
result = sb.table("vapi_debug_logs").select("*").order("created_at", desc=True).limit(20).execute()

if result.data:
    for log in result.data:
        print(f"\n--- {log.get('created_at', 'N/A')} ---")
        print(f"Event: {log.get('event_type')}")
        print(f"Direction: {log.get('call_direction')}")
        print(f"Raw Phone: {log.get('raw_phone')}")
        print(f"Normalized: {log.get('normalized_phone')}")
        print(f"Lookup: {log.get('lookup_result')}")
        print(f"Name Found: {log.get('customer_name_found')}")
        print(f"Notes: {log.get('notes')}")
else:
    print("No debug logs found - table may be empty")
    print("This means assistant-request events are NOT being triggered")
    print("Or the debug table doesn't exist yet")

# Also check conversation_logs for voice
print("\n\n=== CONVERSATION LOGS (Voice, Last 10) ===")
result2 = sb.table("conversation_logs").select("*").eq("channel", "voice").order("created_at", desc=True).limit(10).execute()

if result2.data:
    for log in result2.data:
        print(f"\n{log.get('created_at', 'N/A')} - {log.get('direction')}")
        print(f"Phone: {log.get('phone_number')}")
        print(f"Message: {str(log.get('message', ''))[:100]}...")
else:
    print("No voice conversation logs found")
