
import os
import requests
import json

def check_social_profiles():
    api_key = os.environ.get("AYRSHARE_API_KEY")
    if not api_key:
        print("❌ AYRSHARE_API_KEY not set.")
        return
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        r = requests.get("https://app.ayrshare.com/api/user", headers=headers)
        data = r.json()
        
        print("\n--- AYRSHARE DISCOVERY ---")
        profiles = data.get("profileData", [])
        if not profiles:
            print("📭 No profiles connected found in API response.")
            print(json.dumps(data, indent=2))
            return

        for profile in profiles:
            platform = profile.get("platform", "Unknown").upper()
            handle = profile.get("handle") or profile.get("display_name") or profile.get("title")
            print(f"- {platform}: @{handle}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_social_profiles()
