# snap_deploy.py
# Goal: Replicate the GHL Max Suite for a new client in under 60 seconds.

import os
import sys
import subprocess

def snap_deploy(client_name, ghl_api_key, supabase_url, supabase_key):
    print(f"🚀 SNAPPING: {client_name}")
    
    # 1. Create Modal Secret for Client
    secret_name = f"vault-{client_name.lower().replace(' ', '-')}"
    print(f"--- Creating Secret: {secret_name}")
    subprocess.run([
        "python", "-m", "modal", "secret", "create", secret_name,
        f"GHL_API_KEY={ghl_api_key}",
        f"SUPABASE_URL={supabase_url}",
        f"SUPABASE_SERVICE_ROLE_KEY={supabase_key}"
    ])
    
    # 2. Update deploy.py to reference this secret (Temp file)
    with open("deploy.py", "r") as f:
        content = f.read()
    
    new_content = content.replace('VAULT = modal.Secret.from_name("agency-vault")', f'VAULT = modal.Secret.from_name("{secret_name}")')
    
    temp_deploy = f"deploy_{client_name.lower().replace(' ', '_')}.py"
    with open(temp_deploy, "w") as f:
        f.write(new_content)
    
    # 3. Deploy to Modal
    print(f"--- Deploying {temp_deploy} to Modal...")
    subprocess.run(["python", "-m", "modal", "deploy", temp_deploy])
    
    # 4. Cleanup
    os.remove(temp_deploy)
    print(f"✅ SUCCESS: {client_name} is LIVE on Modal.")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python snap_deploy.py <client_name> <ghl_api_key> <supabase_url> <supabase_key>")
    else:
        snap_deploy(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
