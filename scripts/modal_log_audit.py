import modal
from deploy import image, VAULT

app = modal.App("vapi-audit")

@app.function(image=image, secrets=[VAULT])
def check_vapi_logs():
    from modules.database.supabase_client import get_supabase
    import json
    
    sb = get_supabase()
    if not sb:
        print("❌ Supabase client failed")
        return
        
    print("🔍 Fetching last 5 Vapi debug logs...")
    r = sb.table('vapi_debug_logs').select('*').order('created_at', desc=True).limit(5).execute()
    
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
            prompt = overrides.get('systemPrompt', '')
            if prompt:
                # Check for "Maya" and "Review Gatekeeper" in prompt
                has_maya = "Maya" in prompt
                has_gatekeeper = "Review Gatekeeper" in prompt
                print(f"Identity Check: {'✅ Maya Found' if has_maya else '❌ No Maya'}")
                print(f"Knowledge Check: {'✅ Gatekeeper Found' if has_gatekeeper else '❌ No Gatekeeper'}")
                print(f"Prompt Start: {prompt[:150]}...")
            else:
                print("Prompt: MISSING")
        else:
            print("Overrides: MISSING")

if __name__ == "__main__":
    with app.run():
        check_vapi_logs.remote()
