import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_PRIVATE_KEY")
print(f"Using Key: {API_KEY[:5]}...{API_KEY[-5:]}")

try:
    res = requests.get("https://api.vapi.ai/phone-number", headers={"Authorization": f"Bearer {API_KEY}"})
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")
