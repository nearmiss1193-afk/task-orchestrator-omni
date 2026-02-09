import requests
import json

URL = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"

payload = {
    "message": {
        "type": "assistant-request",
        "call": {
            "direction": "inbound",
            "customerNumber": "+13529368152"
        },
        "customer": {
            "number": "+13529368152"
        }
    }
}

def mock_webhook():
    print(f"🚀 Mocking Vapi Webhook for +13529368152...")
    try:
        resp = requests.post(URL, json=payload, timeout=30)
        print(f"📡 Status Code: {resp.status_code}")
        print(f"📄 Response Body:\n{json.dumps(resp.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Mock failed: {e}")

if __name__ == "__main__":
    mock_webhook()
