import modal

app = modal.App("maya-audit")
image = modal.Image.debian_slim().pip_install("supabase")
VAULT = modal.Secret.from_name("sovereign-vault")

@app.function(image=image, secrets=[VAULT])
def check_maya():
    import os
    from supabase import create_client
    
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    
    print("\n🔍 MAYA SYNC CHECK (vapi_debug_logs):")
    # Search for anything related to the demo number
    r = sb.table("vapi_debug_logs").select("*").ilike("notes", "%customer%").order("created_at", desc=True).limit(5).execute()
    
    if not r.data:
        print("⚠️ No recent logs found.")
        return
        
    for i, row in enumerate(r.data):
        print(f"\n[{i+1}] {row.get('created_at')} | {row.get('event_type')}")
        overrides = row.get("assistant_overrides_sent")
        if overrides:
            prompt = overrides.get("systemPrompt", "")
            has_maya = "Maya" in prompt
            print(f"    Maya Detected: {'✅ YES' if has_maya else '❌ NO'}")
            print(f"    First Message: {overrides.get('firstMessage')}")
            
            # Check for the new V2 format
            if "assistant" in overrides:
                print("    Format: ✅ V2 (Full Assistant Object)")
            else:
                print("    Format: ❌ V1 (Overrides Only)")
        else:
            print("    Overrides: MISSING")

if __name__ == "__main__":
    with app.run():
        check_maya.remote()
