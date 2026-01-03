
import modal
import deploy
import os
import requests
import json

app = deploy.app

@app.local_entrypoint()
def main():
    print("🔎 DEBUG: GHL TOKEN CHECK")
    res = check_token.remote()
    print(res)

@app.function(image=deploy.image, secrets=[deploy.VAULT])
def check_token():
    token = os.environ.get("GHL_API_TOKEN")
    if not token:
        return "❌ NO TOKEN FOUND IN ENV"
    
    print(f"🔑 Token found: {token[:15]}...")
    
    headers = {
        'Authorization': f'Bearer {token}', 
        'Version': '2021-04-15', 
        'Content-Type': 'application/json'
    }
    
    # Check Location
    try:
        url = "https://services.leadconnectorhq.com/locations/v2/me" # Standard V2 endpoint
        res = requests.get(url, headers=headers)
        return f"📡 API Response ({res.status_code}): {res.text}"
    except Exception as e:
        return f"❌ Request Failed: {str(e)}"
