
import modal
import os
import json
from supabase import create_client

app = modal.App("debug-connection")
image = modal.Image.debian_slim().pip_install("supabase", "gotrue")
VAULT = modal.Secret.from_name("agency-vault")

@app.function(image=image, secrets=[VAULT])
def check_connection():
    print("--- START DEBUG ---")
    
    # 1. Check Env Vars
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    # Also check for the credential used locally
    alt_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    
    print(f"ENV[SUPABASE_URL]: {url[:15]}..." if url else "Not Set")
    print(f"ENV[NEXT_PUBLIC_SUPABASE_URL]: {alt_url[:15]}..." if alt_url else "Not Set")
    print(f"ENV[SUPABASE_SERVICE_ROLE_KEY]: {key[:10]}..." if key else "Not Set")
    
    target_url = url or alt_url
    if not target_url or not key:
        print("CRITICAL: Missing Credentials in Vault.")
        return
        
    # 2. Try Connection
    print(f"Connecting to {target_url}...")
    try:
        supabase = create_client(target_url, key)
        print("Client Created.")
        
        # 3. Test Select
        print("Attempting SELECT from brain_logs...")
        res = supabase.table("brain_logs").select("*").limit(1).execute()
        print("SUCCESS: Read Cloud Logs.")
        print(f"Data: {res.data}")
        
    except Exception as e:
        print(f"FAILURE: {str(e)}")
        # Check contacts as fallback
        try:
             res = supabase.table("contacts_master").select("*").limit(1).execute()
             print("Fallback: contacts_master access OK.")
        except:
             print("Fallback: contacts_master ALSO failed.")
             
    print("--- END DEBUG ---")

@app.local_entrypoint()
def main():
    check_connection.remote()
