
import os
from ayrshare import SocialPost

def check_connected_profiles():
    api_key = os.environ.get("AYRSHARE_API_KEY")
    if not api_key:
        print("❌ AYRSHARE_API_KEY not found in environment.")
        return
        
    try:
        sp = SocialPost(api_key)
        # sp.user() returns info about the connected accounts
        user_info = sp.user()
        
        print("\n--- CONNECTED SOCIAL PROFILES (AYRSHARE) ---")
        profiles = user_info.get("profileData", [])
        if not profiles:
            print("📭 No profiles connected to this Ayrshare account.")
            return

        for profile in profiles:
            print(f"- {profile.get('platform', 'Unknown').upper()}: {profile.get('title', 'No Title')} ({profile.get('handle', 'No Handle')})")
            
    except Exception as e:
        print(f"❌ Error fetching profiles from Ayrshare: {e}")

if __name__ == "__main__":
    check_connected_profiles()
