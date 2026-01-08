import os, requests, json
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
VAPI_API_KEY = os.getenv('VAPI_API_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
USER_PHONE = os.getenv('TEST_PHONE')  # user's phone number for testing

if not VAPI_API_KEY or not VAPI_PRIVATE_KEY:
    raise RuntimeError('VAPI credentials not set')

# Sarah 3.1: The 'Empathetic Rebel' Optimization
prospecting_script = """
Role: Sarah, the Empathetic Rebel. 
Context: Calling HVAC owners in Florida.
Hook: "Hey [Name]? Sarah here. Look, I saw [Company Name] and honestly, I'm calling because you're one of the few who actually seems to have their act together. But let's be real—even the best teams miss revenue when the phones get slammed at 2 PM or dead quiet at 2 AM. Got a sec for a quick theory on how to fix that?"

Style: Zero corporate. Use "Look", "Actually", "Um". No "Thanks for connecting".
Mission: Address 'Receptionist' or 'No Problem' objections with wit.
"""

# Create the call via Vapi API
url = 'https://api.vapi.ai/call/phone' 
payload = {
    "assistantId": "1a797f12-e2dd-4f7f-b2c5-08c38c74859a", # Sarah 3.1 in Vapi
    "phoneNumberId": os.getenv('VAPI_PHONE_NUMBER_ID', '8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e'),
    "customer": {
        "number": USER_PHONE,
        "name": "Test Call"
    }
}
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}
try:
    print(f"Triggering Sarah 3.1 call to {USER_PHONE}...")
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print('Vapi call response status:', response.status_code)
    print('Response body:', response.text)
except Exception as e:
    print(f"Error triggering call: {e}")
