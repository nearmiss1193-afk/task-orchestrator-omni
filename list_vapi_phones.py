import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
url = "https://api.vapi.ai/phone-number"

headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    numbers = response.json()
    
    print(f"Found {len(numbers)} numbers:")
    for n in numbers:
        print(f"Number: {n.get('number')} | ID: {n.get('id')} | AreaCode: {n.get('number', '')[:3]}")
        
    with open("vapi_phones.json", "w") as f:
        json.dump(numbers, f, indent=2)
        
except Exception as e:
    print(f"Error listing numbers: {e}")
    if hasattr(e, 'response') and e.response:
        print(e.response.text)
