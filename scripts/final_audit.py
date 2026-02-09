import os
import sys
from dotenv import load_dotenv
sys.path.append(os.getcwd()) # Ensure core/modules are findable
from modules.database.supabase_client import get_supabase

# Load both possible secret files
load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

phone = "+13529368152"

def audit_number(phone_num):
    sb = get_supabase()
    print(f"🔍 Auditing: {phone_num}")
    
    # 1. Check customer_memory
    print("\n[1] customer_memory:")
    res = sb.table("customer_memory").select("*").eq("phone_number", phone_num).execute()
    if res.data:
        for row in res.data:
            print(f" - Found: {row.get('customer_name')} | Context: {str(row.get('context_summary'))[:200]}...")
    else:
        print(" - NOT FOUND in customer_memory")

    # 2. Check vapi_debug_logs
    print("\n[2] vapi_debug_logs (last 5):")
    res = sb.table("vapi_debug_logs").select("*").eq("normalized_phone", phone_num).order("created_at", desc=True).limit(5).execute()
    if res.data:
        for row in res.data:
            print(f" - {row.get('created_at')}: {row.get('event_type')} | Result: {row.get('lookup_result')}")
    else:
        print(" - NO ENTRIES in vapi_debug_logs")

    # 3. Check conversation_logs
    print("\n[3] conversation_logs (last 5):")
    res = sb.table("conversation_logs").select("*").eq("phone_number", phone_num).order("created_at", desc=True).limit(5).execute()
    if res.data:
        for row in res.data:
            print(f" - {row.get('created_at')}: {row.get('channel')} {row.get('direction')} | Msg: {str(row.get('message'))[:50]}...")
    else:
        print(" - NO ENTRIES in conversation_logs")

if __name__ == "__main__":
    audit_number(phone)
