
import requests

def check(url):
    print(f"Checking {url}...")
    try:
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("✅ SUCCESS")
            print(r.text[:100])
        else:
            print("❌ FAIL")
            print(f"Content: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

check("https://nearmiss1193-afk--ghl-omni-light-hello.modal.run")
check("https://nearmiss1193-afk--ghl-omni-light-hvac-landing.modal.run")
