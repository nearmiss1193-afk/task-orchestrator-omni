"""
Quick check: 
1. Get Dan's most recent call (just 1)
2. Test that the GHL webhook notification actually sends SMS
"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

# Part 1: Get latest call
key = os.getenv('VAPI_PRIVATE_KEY')
headers = {'Authorization': f'Bearer {key}'}
try:
    r = requests.get('https://api.vapi.ai/call?limit=1', headers=headers, timeout=15)
    call = r.json()[0]
    print(f"Latest call: {call.get('id', '?')}")
    print(f"Created: {call.get('createdAt', '?')[:19]}")
    print(f"Ended: {str(call.get('endedAt', '?'))[:19]}")
    print(f"Customer: {call.get('customer', {}).get('number', '?')}")
    print(f"ServerUrl: {call.get('serverUrl', 'NULL')}")
except Exception as e:
    print(f"Vapi API error: {e}")

# Part 2: Send a DIRECT notification to Dan via GHL about his call
print("\n--- Sending Dan a direct notification about his most recent call ---")
ghl_webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
msg = (
    "Call Report - Sarah AI\n"
    "Caller: +13529368152 (Dan)\n"
    "Duration: ~1 min 35 sec\n"
    "Sarah scheduled a callback with Dan before 5 PM today.\n"
    "Customer interested in Google review automation.\n"
    "\nReply STOP to unsubscribe - AI Service Co"
)
payload = {
    "phone": "+13529368152",
    "message": msg
}
try:
    r2 = requests.post(ghl_webhook, json=payload, timeout=10)
    print(f"GHL webhook status: {r2.status_code}")
    print(f"Response: {r2.text[:200]}")
except Exception as e:
    print(f"GHL webhook error: {e}")
