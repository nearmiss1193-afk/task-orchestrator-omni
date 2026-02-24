import requests

def check_endpoint():
    url = 'https://nearmiss1193-afk--ghl-omni-automation-system-heartbeat.modal.run'
    print(f"Pinging {url}...")
    try:
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text[:200]}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    check_endpoint()
