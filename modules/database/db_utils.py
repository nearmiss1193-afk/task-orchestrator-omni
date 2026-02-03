
import os
import requests

# ==== DATABASE CONFIGURATION ====
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def supabase_request(method, table, params=None, json_data=None):
    """
    Centralized Supabase REST API wrapper to avoid circular imports.
    """
    if not SUPABASE_KEY:
        print("[Supabase Error] No API Key configuration found.")
        return None
        
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    try:
        if method == "GET":
            res = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            res = requests.post(url, headers=headers, json=json_data)
        elif method == "PATCH":
            res = requests.patch(url, headers=headers, json=json_data, params=params)
        elif method == "DELETE":
            res = requests.delete(url, headers=headers, params=params)
        else:
            return None
            
        if res.status_code in [200, 201]:
            try:
                return res.json()
            except:
                return {"status": "success"}
        else:
            print(f"[Supabase Error] {res.status_code}: {res.text}")
            return None
    except Exception as e:
        print(f"[Supabase Exception] {e}")
        return None
