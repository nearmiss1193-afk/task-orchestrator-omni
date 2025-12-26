import os
import requests
from dotenv import load_dotenv

load_dotenv(".env.local")

def check_supabase_rest():
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }
    
    # Try to list tables via PostgREST OpenAPI (usually /rest/v1/)
    try:
        res = requests.get(f"{url}/rest/v1/", headers=headers)
        if res.status_code == 200:
            print("✅ Supabase REST: Online.")
            # Check if contacts_master is in the definitions
            if "contacts_master" in res.text:
                print("✅ Table 'contacts_master': Exists.")
            else:
                print("❌ Table 'contacts_master': Missing!")
        else:
            print(f"❌ Supabase REST: Failed ({res.status_code}). {res.text}")
    except Exception as e:
        print(f"❌ Supabase REST: Error. {str(e)}")

def check_gemini_models():
    api_key = os.environ.get("GOOGLE_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            models = [m['name'] for m in res.json().get('models', [])]
            print(f"✅ Gemini Models Found: {', '.join(models[:3])}...")
        else:
            print(f"❌ Gemini Models List: Failed ({res.status_code}). {res.text}")
    except Exception as e:
        print(f"❌ Gemini Models List: Error. {str(e)}")

if __name__ == "__main__":
    check_supabase_rest()
    check_gemini_models()
