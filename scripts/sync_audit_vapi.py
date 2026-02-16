from modules.database.supabase_client import get_supabase
import json
from datetime import datetime

def debug_vapi():
    print("🎯 SYNC AUDIT: Checking Vapi Hits in Supabase...")
    sb = get_supabase()
    if not sb:
        print("❌ FAILED: Supabase client not initialized.")
        return
        
    # Get last 10 hits
    r = sb.table("vapi_debug_logs").select("*").order("created_at", desc=True).limit(10).execute()
    
    if not r.data:
        print("⚠️ No data in vapi_debug_logs.")
        return
        
    print(f"📊 Found {len(r.data)} recent webhooks.")
    for i, row in enumerate(r.data):
        ts = row.get("created_at")
        phone = row.get("normalized_phone")
        mode = row.get("call_mode")
        event = row.get("event_type")
        notes = row.get("notes")
        
        print(f"\n[{i+1}] {ts} | {event} | Phone: {phone} | Mode: {mode}")
        print(f"    Notes: {notes}")
        
        overrides = row.get("assistant_overrides_sent")
        if overrides:
            first = overrides.get("firstMessage", "NONE")
            print(f"    FirstMsg: {first}")
            sys_msg = overrides.get("systemPrompt", "")
            if "Maya" in sys_msg:
                print("    Persona: ✅ MAYA DETECTED in Prompt")
            else:
                print("    Persona: ❌ SARAH/DEFAULT in Prompt")
                
            # If there's an 'assistant' key (my recent fix)
            assistant_obj = row.get("assistant_overrides_sent", {}).get("assistant")
            if assistant_obj:
                print("    Response Format: ✅ V2 (Standard Assistant Object)")
            else:
                print("    Response Format: ❌ V1 (assistantOverrides only)")
        else:
            print("    Overrides: MISSING")

if __name__ == "__main__":
    debug_vapi()
