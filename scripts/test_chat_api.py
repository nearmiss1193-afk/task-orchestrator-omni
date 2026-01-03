
import requests

URL = "http://localhost:3000/api/chat"

def test(msg):
    print(f"\n🧪 Sending: '{msg}'")
    try:
        r = requests.post(URL, json={"message": msg}, timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json().get('response')[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

test("search for pest control competitors")
test("tell Antigravity to secure the perimeter")
test("what is the system status?")
