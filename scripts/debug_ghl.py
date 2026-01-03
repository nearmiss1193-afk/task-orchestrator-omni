import requests
import os
import json

# HARDCODED VERIFIED TOKEN
TOKEN = "pit-8c6cabd9-2c4a-4581-a664-ca2b6200e199"

def check_ghl():
    print(f"🕵️ DEBUGGING GHL API...")
    
    url = "https://services.leadconnectorhq.com/contacts/?limit=10&locationId=RnK4OjX0oDcqtWw0VyLr"
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Version': '2021-07-28',
        'Content-Type': 'application/json'
    }
    
    try:
        res = requests.get(url, headers=headers)
        print(f"📡 STATUS CODE: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            contacts = data.get('contacts', [])
            meta = data.get('meta', {})
            print(f"✅ SUCCESS. Found {len(contacts)} contacts in batch.")
            print(f"📊 META: {json.dumps(meta, indent=2)}")
            
            if contacts:
                print(f"👤 Sample Contact 1: {contacts[0].get('email')} / {contacts[0].get('id')}")
            else:
                print("⚠️  Account appears empty (0 contacts returned).")
        else:
            print(f"❌ ERROR RAW: {res.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    check_ghl()
