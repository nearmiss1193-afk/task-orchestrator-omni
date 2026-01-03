import requests
url = "https://jeanie-makable-deve-deon.ngrok-free.dev/landing/hvac.html"
print(f"Testing: {url}")
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = requests.get(url, timeout=10, verify=False)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        if "(863) 213-2505" in r.text:
            print("✅ Phone Number Verified")
        else:
            print("❌ Phone Number Missing in Response")
        if "Most Popular" in r.text:
             print("✅ Pricing Verified")
        else:
             print("❌ Pricing Missing")
        if "Text Us" in r.text:
             print("✅ Chat Verified")
        else:
             print("❌ Chat Missing")
    else:
        print(f"❌ Failed: {r.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
