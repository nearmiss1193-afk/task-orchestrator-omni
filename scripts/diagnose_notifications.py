"""Diagnose notification pipeline"""
import requests, json

# 1. Test GHL webhook with Dan's number
GHL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
DAN_PHONE = "+13529368152"

r1 = requests.post(GHL_WEBHOOK, json={
    "phone": DAN_PHONE,
    "message": "TEST ALERT: If you see this, GHL notifications are working."
}, timeout=10)
print(f"GHL webhook test: {r1.status_code} - {r1.text[:200]}")

# 2. Test Modal vapi_webhook endpoint
MODAL_URL = "https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run"
r2 = requests.post(MODAL_URL, json={
    "message": {"type": "end-of-call-report", "call": {"direction": "inbound", "customer": {"number": "+18638129362"}}, "summary": "TEST: Christina from Call Me Now asked for Dan.", "transcript": "this is Christina at Call Me Now"}
}, timeout=15)
print(f"\nModal vapi_webhook: {r2.status_code} - {r2.text[:300]}")

# 3. Check if Dan is a GHL contact
GHL_API = "https://services.leadconnectorhq.com/contacts/search"
# We don't have GHL API key handy, so just report what we know
print(f"\nDIAGNOSIS:")
print(f"  GHL webhook response: {r1.status_code}")
print(f"  Modal webhook response: {r2.status_code}")
if r1.status_code == 422:
    print("  --> GHL 422 = Dan's number not in GHL as a contact")
    print("  --> Fix: Import Dan's number as a contact in GHL")
elif r1.status_code == 200:
    print("  --> GHL accepted the request - should deliver SMS")
if r2.status_code >= 400:
    print(f"  --> Modal endpoint error = deploy may be broken or stale")
elif r2.status_code == 200:
    print("  --> Modal endpoint working - but may not be getting triggered by Vapi")
