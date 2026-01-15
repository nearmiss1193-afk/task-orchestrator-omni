"""Check Vapi phone configuration for inbound calls"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('VAPI_PRIVATE_KEY')

print("=== VAPI PHONE NUMBERS ===")
r = requests.get('https://api.vapi.ai/phone-number', headers={'Authorization': f'Bearer {key}'})
phones = r.json()

for p in phones:
    print(f"\nNumber: {p.get('number')}")
    print(f"  ID: {p.get('id')}")
    print(f"  Assistant ID: {p.get('assistantId', 'NOT SET - PROBLEM!')}")
    print(f"  Status: {p.get('status')}")
    print(f"  Provider: {p.get('provider')}")

print("\n=== SARAH ASSISTANT ===")
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
r2 = requests.get(f'https://api.vapi.ai/assistant/{SARAH_ID}', headers={'Authorization': f'Bearer {key}'})
if r2.status_code == 200:
    sarah = r2.json()
    print(f"Name: {sarah.get('name')}")
    print(f"Model: {sarah.get('model', {}).get('provider')}")
    print(f"Voice: {sarah.get('voice', {}).get('provider')}")
    print(f"First Message: {sarah.get('firstMessage', '')[:100]}...")
else:
    print(f"Error: {r2.status_code}")
