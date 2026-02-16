from modules.database.supabase_client import get_supabase
import json

def check_logs():
    sb = get_supabase()
    if not sb:
        print("❌ Supabase client failed")
        return
        
    print("🔍 Fetching last 3 Vapi debug logs...")
    r = sb.table('vapi_debug_logs').select('*').order('created_at', desc=True).limit(3).execute()
    
    if not r.data:
        print("⚠️ No logs found in vapi_debug_logs")
        return
        
    for i, row in enumerate(r.data):
        print(f"\n--- LOG #{i+1} ({row.get('created_at')}) ---")
        print(f"Event: {row.get('event_type')}")
        print(f"Phone: {row.get('normalized_phone')}")
        print(f"Mode: {row.get('call_mode')}")
        print(f"Direction: {row.get('call_direction')}")
        print(f"Notes: {row.get('notes')}")
        
        overrides = row.get('assistant_overrides_sent')
        if overrides:
            print(f"First Message: {overrides.get('firstMessage')}")
            # Just show start of prompt to verify identity
            prompt = overrides.get('systemPrompt', '')
            if prompt:
                print(f"Prompt Start: {prompt[:200]}...")
            else:
                print("Prompt: MISSING")
        else:
            print("Overrides: MISSING")

if __name__ == '__main__':
    check_logs()
