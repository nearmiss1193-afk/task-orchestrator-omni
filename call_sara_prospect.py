import os, requests, json

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

# Create the call via Vapi API (simplified example)
url = 'https://api.vapi.ai/v1/calls'
payload = {
    "to": USER_PHONE,
    "from": os.getenv('VAPI_PHONE_NUMBER_ID'),
    "script": prospecting_script,
    "agent": "sara",
    "metadata": {"purpose": "prospecting_demo"}
}
headers = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}
response = requests.post(url, headers=headers, json=payload)
print('Vapi call response status:', response.status_code)
print('Response body:', response.text)
