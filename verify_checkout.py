
import requests
import json
import sys

BASE_URL = "https://empire-sovereign-cloud.vercel.app/api/create-checkout-session"

def verify():
    print(f"Testing Checkout Creation at {BASE_URL}")
    payload = {
        "plan": "starter",
        "email": "verification_bot@empire.connected.world"
    }
    
    try:
        res = requests.post(BASE_URL, json=payload, timeout=10)
        print(f"Status Code: {res.status_code}")
        print(f"Response Body: {res.text}")
        print()
        
        if res.status_code == 200:
            data = res.json()
            print(f"Parsed JSON: {json.dumps(data, indent=2)}")
            print()
            
            if data.get("status") == "success" and "url" in data:
                print("✅ SUCCESS: Stripe Checkout Session Created.")
                print(f"Checkout URL: {data['url']}")
                return True
            else:
                print("❌ FAILURE: API returned 200 but missing success/url.")
                if "message" in data:
                    print(f"Error Message: {data['message']}")
                return False
        else:
            print(f"FAILURE: Unexpected status code {res.status_code}")
            return False
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    success = verify()
    if not success:
        sys.exit(1)
