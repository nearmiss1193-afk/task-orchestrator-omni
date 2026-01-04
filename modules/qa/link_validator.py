
import requests
import sys

def validate_link(url):
    """
    The 'Shopper' Verification Logic.
    Tests if a URL is publicly accessible (Status 200).
    """
    print(f"🕵️ Shopper Inspecting Link: {url}...")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Link is LIVE (Status: 200 OK)")
            return True
        else:
            print(f"   ❌ Link is BROKEN (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Link Failed: Connection Error (Server Down?)")
        return False
    except Exception as e:
        print(f"   ❌ Link Failed: {e}")
        return False

if __name__ == "__main__":
    # Test the 404 URL provided by user
    target = "https://empire-sovereign-cloud.vercel.app"
    is_valid = validate_link(target)
    
    # Also test a known good page if possible, e.g., login or root
    # validate_link("https://google.com")
    
    if not is_valid:
        print("\n⚠️ ALERT: The Landing Page is DOWN. Do not send traffic.")
        sys.exit(1)
