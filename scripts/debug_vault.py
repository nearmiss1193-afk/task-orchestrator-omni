
import modal
import os
from core.image_config import image, VAULT
from core.apps import engine_app as app

@app.function(image=image, secrets=[VAULT])
def debug_vault():
    print("🚀 DIANOSTIC: Checking Modal environment...")
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"URL: {url[:20]}..." if url else "URL: MISSING")
    print(f"KEY: {key[:10]}..." if key else "KEY: MISSING")
    print(f"ROLE KEY: {role_key[:10]}..." if role_key else "ROLE KEY: MISSING")
    
    if not url or not role_key:
        return "FAIL: Missing required Supabase credentials"
    
    from supabase import create_client
    try:
        sb = create_client(url, role_key)
        res = sb.table("contacts_master").select("id").limit(1).execute()
        return f"SUCCESS: Can see {len(res.data)} leads"
    except Exception as e:
        return f"FAIL: Supabase client error: {e}"

if __name__ == "__main__":
    with modal.Retort():
        print(debug_vault.remote())
