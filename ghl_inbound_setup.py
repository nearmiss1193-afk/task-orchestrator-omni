"""
GHL Inbound Webhook Setup - Forwards SMS/calls to Sarah Dispatcher
Configure this URL in GHL Automation Workflows
"""

# =============================================================================
# WEBHOOK URL TO CONFIGURE IN GHL
# =============================================================================
SARAH_DISPATCHER_WEBHOOK = "https://nearmiss1193-afk--sarah-dispatcher-handle-inbound.modal.run"

# =============================================================================
# GHL WORKFLOW SETUP INSTRUCTIONS
# =============================================================================
"""
1. Go to GHL → Automation → Workflows
2. Create new workflow triggered by "Inbound SMS" or "Inbound Call"
3. Add action: "Webhook"
4. Configure webhook:
   - URL: https://nearmiss1193-afk--sarah-dispatcher-handle-inbound.modal.run
   - Method: POST
   - Headers: Content-Type: application/json
   - Body:
     {
       "phone": "{{contact.phone}}",
       "channel": "sms",
       "message": "{{message.body}}"
     }

5. For calls, set channel to "call" and message to the transcription

6. Add another webhook action to send Sarah's response back to the contact:
   - Trigger: After receiving response from dispatcher
   - Action: Send SMS using {{response.response}}
"""

import requests

def test_dispatcher():
    """Test the Sarah dispatcher webhook"""
    r = requests.post(
        SARAH_DISPATCHER_WEBHOOK,
        json={
            "phone": "+18633373705",
            "channel": "sms",
            "message": "Hi, I saw your email. What do you offer?"
        },
        timeout=30
    )
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
    return r.json()


if __name__ == "__main__":
    print("=" * 60)
    print("GHL INBOUND WEBHOOK SETUP")
    print("=" * 60)
    print(f"\nDispatcher URL: {SARAH_DISPATCHER_WEBHOOK}")
    print("\nTesting connection...")
    try:
        result = test_dispatcher()
        print(f"\n✅ Sarah responded: {result.get('response', 'No response')[:100]}...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
