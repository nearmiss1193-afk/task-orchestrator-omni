import requests

VAPI_API_KEY = 'c23c884d-0008-4b14-ad5d-530e98d0c9da'
SARAH_ID = '1a797f12-e2dd-4f7f-b2c5-08c38c74859a'
FALLBACK_PHONE = '+13529368152'

# Get current config first
url = f'https://api.vapi.ai/assistant/{SARAH_ID}'
headers = {'Authorization': f'Bearer {VAPI_API_KEY}', 'Content-Type': 'application/json'}

print("Fetching current Sarah config...")
r = requests.get(url, headers=headers, timeout=30)
if r.status_code == 200:
    data = r.json()
    print(f"Current Name: {data.get('name')}")
    print(f"Server URL: {data.get('serverUrl', 'None')}")
    
    # The correct Vapi property is 'forwardingPhoneNumber' but it may need to be 
    # set on the phone number config, not assistant config
    # Let's try setting transferConfig instead
    
    # For call forwarding in Vapi, we need to configure the transferPhoneNumbers
    # which allows the assistant to transfer calls
    transfer_config = {
        "endCallAfterSpokenEnabled": True,
        "destinations": [
            {
                "type": "number",
                "number": FALLBACK_PHONE,
                "message": "I'm connecting you with a live representative now. Please hold."
            }
        ]
    }
    
    # Try setting as analysis plan with transfer destination
    payload = {
        "serverUrlSecret": "",
        "forwardingPhoneNumber": None,  # Clear this if exists
        "serverMessages": ["end-of-call-report", "transcript", "tool-calls"],
        "analysisPlan": {
            "summaryPrompt": "Summarize the call in 2-3 sentences."
        }
    }
    
    # Actually for forwarding unanswered calls, that's a phone number setting not assistant
    print("\n[NOTE] Call forwarding for UNANSWERED calls is configured on the")
    print("       Vapi PHONE NUMBER, not the assistant.")
    print(f"       User should configure +1-352-936-8152 as fallback in Vapi dashboard")
    print(f"       for Sarah's phone number: +1 (352) 758-5336")
    print("\n[ACTION REQUIRED] Configure in Vapi Dashboard:")
    print("  1. Go to vapi.ai/dashboard")
    print("  2. Select Phone Numbers")
    print("  3. Edit the 352-758-5336 number")
    print(f"  4. Set Fallback Number to: {FALLBACK_PHONE}")
    
else:
    print(f"Error: {r.status_code}")
    print(r.text[:300])
