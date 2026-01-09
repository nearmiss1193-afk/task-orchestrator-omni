# list_vapi_phones.py - List available Vapi phone numbers
import os
from dotenv import load_dotenv
import requests

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")

url = "https://api.vapi.ai/phone-number"
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

res = requests.get(url, headers=headers)

if res.status_code == 200:
    phones = res.json()
    print("=== AVAILABLE VAPI PHONE NUMBERS ===")
    print(f"Total: {len(phones)}")
    print()
    for p in phones:
        phone_id = p.get('id', 'Unknown')
        number = p.get('number', 'No number')
        name = p.get('name', 'Unnamed')
        provider = p.get('provider', 'Unknown')
        print(f"ID: {phone_id}")
        print(f"  Number: {number}")
        print(f"  Name: {name}")
        print(f"  Provider: {provider}")
        print("-" * 40)
else:
    print(f"Error: {res.status_code}")
    print(res.text)
