import requests
import json
import os

VAPI_PRIVATE_KEY = "c23c884d-0008-4b14-ad5d-530e98d0c9da"

def get_phone_numbers():
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    url = "https://api.vapi.ai/phone-number"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        numbers = response.json()
        
        print("📲 Vapi Phone Numbers:")
        if not numbers:
             print("   (No phone numbers found)")
        else:
            for num in numbers:
                 print(f"   - Number: {num.get('number')} | ID: {num.get('id')} | Name: {num.get('name')}")
                 
    except Exception as e:
        print(f"❌ Error fetching numbers: {e}")
        print(response.text)

if __name__ == "__main__":
    get_phone_numbers()
