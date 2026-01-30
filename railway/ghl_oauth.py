
import os
import requests
import json
from supabase import create_client

# CONFIG
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

# GHL APP CREDENTIALS (Sovereign Empire Marketplace App)
CLIENT_ID = os.environ.get("GHL_CLIENT_ID") or "6960484a6f88b50eb5b5a43b" 
CLIENT_SECRET = os.environ.get("GHL_CLIENT_SECRET") 

REDIRECT_URI = "https://empire-unified-backup-production.up.railway.app/ghl/oauth/callback"
SCOPES = [
    "contacts.readonly", "contacts.write",
    "locations.readonly", "locations.write",
    "opportunities.readonly", "opportunities.write",
    "messages.readonly", "messages.write"
]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_auth_url():
    """Generates the GHL OAuth Alpha Authorization URL"""
    scope_str = " ".join(SCOPES)
    url = f"https://marketplace.gohighlevel.com/oauth/chooselocation?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={scope_str}"
    return url

def exchange_code(code):
    """Exchanges authorization code for access and refresh tokens"""
    print(f"🔄 Exchange: Received code {code[:10]}...")
    # Log the receipt of code for debugging
    supabase.table("system_state").upsert({"key": "last_ghl_code", "value": code}, on_conflict="key").execute()
    
    if not CLIENT_SECRET:
        print("❌ Error: GHL_CLIENT_SECRET is missing. Cannot exchange code.")
        return None
    
    url = "https://services.leadconnectorhq.com/oauth/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "user_type": "Location",
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    r = requests.post(url, data=data, headers=headers)
    if r.ok:
        tokens = r.json()
        save_tokens(tokens)
        return tokens
    else:
        print(f"Error {r.status_code}: {r.text}")
        return None

def save_tokens(tokens):
    """Saves tokens to Supabase system_state"""
    # Keys to save: ghl_access_token, ghl_refresh_token, ghl_location_id
    updates = [
        {"key": "ghl_access_token", "value": tokens.get("access_token")},
        {"key": "ghl_refresh_token", "value": tokens.get("refresh_token")},
        {"key": "ghl_location_id", "value": tokens.get("locationId")}
    ]
    
    for item in updates:
        supabase.table("system_state").upsert(item, on_conflict="key").execute()
    print("✅ GHL Tokens saved to Supabase")

if __name__ == "__main__":
    print("--- GHL OAUTH HANDSHAKE ---")
    print(f"Authorization URL: {generate_auth_url()}")
