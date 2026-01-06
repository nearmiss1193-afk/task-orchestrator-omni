import os, requests, json
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
VAPI_API_KEY = os.getenv('VAPI_API_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
USER_PHONE = os.getenv('TEST_PHONE')  # user's phone number for testing

if not VAPI_API_KEY or not VAPI_PRIVATE_KEY:
    raise RuntimeError('VAPI credentials not set')

# Define the prospecting script for Sara
prospecting_script = """
You are Sara, an AI sales prospecting assistant.
Introduce yourself, ask about the prospect's HVAC needs, and schedule a call.
Keep it friendly and concise.
"""

# Create the call via Vapi API
url = 'https://api.vapi.ai/call/phone' # Correct outbound endpoint
payload = {
    "assistantId": "1a797f12-e2dd-4f7f-b2c5-08c38c74859a", # Sarah the Spartan
    "phoneNumberId": os.getenv('VAPI_PHONE_NUMBER_ID'),
    "customer": {
        "number": USER_PHONE,
        "name": "Homeheart Hvac"
    }
}
headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}
try:
    print(f"Triggering call to {USER_PHONE}...")
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print('Vapi call response status:', response.status_code)
    print('Response body:', response.text)
except Exception as e:
    print(f"Error triggering call: {e}")
