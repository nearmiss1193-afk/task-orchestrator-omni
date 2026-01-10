import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_FROM_NUMBER')

print(f"🔌 Importing Twilio Number {TWILIO_NUMBER} to Vapi...")

url = "https://api.vapi.ai/phone-number"

payload = {
    "provider": "twilio",
    "number": TWILIO_NUMBER,
    "twilioAccountSid": TWILIO_ACCOUNT_SID,
    "twilioAuthToken": TWILIO_AUTH_TOKEN,
    "name": "Empire Invoice (Twilio)"
}

headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(response.text)
    
    if response.status_code == 201:
        data = response.json()
        new_id = data.get('id')
        print(f"✅ SUCCESS! New Phone ID: {new_id}")
        
        # Append to .env so it persists
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'a') as f:
            f.write(f"\n# Twilio number imported to Vapi (unlimited calls)\nVAPI_TWILIO_PHONE_ID={new_id}\n")
        print(f"✅ Saved VAPI_TWILIO_PHONE_ID to .env")
    else:
        print("❌ Import Failed.")
        print("Try importing manually via Vapi Dashboard: https://dashboard.vapi.ai/phone-numbers")

except Exception as e:
    print(f"Error: {e}")
