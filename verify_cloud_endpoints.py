
import requests
import sys

# Base format: [username]--[function_name].modal.run
# Assuming username is 'nearmiss1193-afk' based on user report
BASE_URL = "https://nearmiss1193-afk--{}.modal.run"

ENDPOINTS = [
    "hvac-landing",
    "plumber-landing",
    "roofer-landing",
    "electrician-landing",
    "solar-landing",
    "landscaping-landing",
    "pest-landing",
    "cleaning-landing",
    "restoration-landing",
    "autodetail-landing"
]

def verify_endpoints():
    print("☁️ Verifying Cloud Endpoints...")
    failed = []
    
    for ep in ENDPOINTS:
        url = BASE_URL.format(ep)
        try:
            print(f"   Checking {url}...", end=" ")
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                print("✅ ONLINE")
            else:
                print(f"❌ FAILED ({res.status_code})")
                failed.append(ep)
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed.append(ep)
            
    if failed:
        print("\n⚠️ FAILURES DETECTED:")
        for f in failed:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("\n🎉 All Endpoints Operational.")
        sys.exit(0)

if __name__ == "__main__":
    verify_endpoints()
