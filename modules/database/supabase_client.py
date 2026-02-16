import os
from supabase import create_client, Client

# Initialize Client
def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    # THE SOVEREIGN LAW (Feb 15): Never use the anon key for backend updates.
    # Service role key is required to bypass RLS.
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        return None
        
    return create_client(url, key)

# Helper to verify connection
def check_connection():
    try:
        sb = get_supabase()
        if not sb: return False
        # Simple health check (assuming leads table might not exist yet, we check something generic or just client init)
        # We'll just return True if client init didn't throw
        return True
    except Exception as e:
        print(f"❌ Supabase Connection Failed: {e}")
        return False
