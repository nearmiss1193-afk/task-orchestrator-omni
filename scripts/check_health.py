import os
import requests
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env.local")

def check_supabase():
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    print(f"--- Debug Supabase ---")
    print(f"URL: {url[:20]}...")
    print(f"Key: {key[:10]}...{key[-10:]}")
    try:
        supabase = create_client(url, key)
        # Try a simple select
        res = supabase.table("contacts_master").select("*").limit(1).execute()
        print(f"✅ Supabase: Connected. Found {len(res.data)} sample record(s).")
        return True
    except Exception as e:
        print(f"❌ Supabase: Failed. Type: {type(e).__name__} | Error: {str(e)}")
        return False

def check_ghl():
    token = os.environ.get("GHL_API_TOKEN")
    location_id = os.environ.get("GHL_LOCATION_ID")
    try:
        # Check location health
        url = f"https://services.leadconnectorhq.com/locations/{location_id}"
        headers = {"Authorization": f"Bearer {token}", "Version": "2021-07-02"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            print(f"✅ GHL API: Connected. Location: {res.json().get('location', {}).get('name')}")
            return True
        else:
            print(f"❌ GHL API: Failed ({res.status_code}). {res.text}")
            return False
    except Exception as e:
        print(f"❌ GHL API: Error. {str(e)}")
        return False

def check_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": "health check"}]}]})
        if res.status_code == 200:
            print("✅ Gemini AI: Online.")
            return True
        else:
            print(f"❌ Gemini AI: Failed ({res.status_code}).")
            return False
    except Exception as e:
        print(f"❌ Gemini AI: Error. {str(e)}")
        return False

if __name__ == "__main__":
    print("--- 🛡️ SYSTEM HEALTH CHECK ---")
    s = check_supabase()
    g = check_ghl()
    ai = check_gemini()
    
    if all([s, g, ai]):
        print("\n🚀 ALL SYSTEMS NOMINAL. READY FOR WHITELABEL DEPLOYMENT.")
    else:
        print("\n⚠️ WARNING: Some systems are offline. Check logs.")
