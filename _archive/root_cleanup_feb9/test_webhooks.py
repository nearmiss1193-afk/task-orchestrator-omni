"""
Test both GHL webhook URLs to see which is working
"""
import requests

# Webhook URL 1 - From .env file (should be correct)
WEBHOOK_1 = "https://services.leadconnectorhq.com/hooks/uFYcZA7Zk6EcBze5B4oH/webhook-trigger/4ac9b8e9-d444-461d-840b-a14ebf09c4dc"

# Webhook URL 2 - From reliable_email.py (possibly old)
WEBHOOK_2 = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt"

# Test payload
test_payload = {
    "email": "nearmiss1193@gmail.com",  # Send to yourself for testing
    "from_name": "Test Sender",
    "from_email": "owner@aiserviceco.com",
    "subject": "TEST: GHL Webhook Test - Please Confirm Receipt",
    "html_body": "<h1>GHL Webhook Test</h1><p>If you receive this, the webhook is working!</p><p>Timestamp: Feb 5, 2026 12:15 PM EST</p>"
}

print("=" * 60)
print("GHL WEBHOOK URL TEST")
print("=" * 60)

# Test Webhook 1 (.env)
print("\n📧 Testing Webhook 1 (.env version)...")
print(f"URL: {WEBHOOK_1[:50]}...")
try:
    r = requests.post(WEBHOOK_1, json=test_payload, timeout=30)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text[:200] if r.text else 'Empty'}")
    if r.status_code in [200, 201, 204]:
        print("✅ Webhook 1 ACCEPTED the request")
    else:
        print("❌ Webhook 1 REJECTED the request")
except Exception as e:
    print(f"❌ Webhook 1 ERROR: {e}")

# Test Webhook 2 (reliable_email.py)
print("\n📧 Testing Webhook 2 (reliable_email.py version)...")
print(f"URL: {WEBHOOK_2[:50]}...")
try:
    r = requests.post(WEBHOOK_2, json=test_payload, timeout=30)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text[:200] if r.text else 'Empty'}")
    if r.status_code in [200, 201, 204]:
        print("✅ Webhook 2 ACCEPTED the request")
    else:
        print("❌ Webhook 2 REJECTED the request")
except Exception as e:
    print(f"❌ Webhook 2 ERROR: {e}")

print("\n" + "=" * 60)
print("CHECK YOUR EMAIL (nearmiss1193@gmail.com) FOR THE TEST!")
print("=" * 60)
