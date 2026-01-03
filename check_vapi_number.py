
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_PRIVATE_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_assistant_id(name):
    res = requests.get("https://api.vapi.ai/assistant", headers=HEADERS)
    for a in res.json():
        if a.get("name") == name:
            return a.get("id")
    return None

def check_numbers():
    print("🔍 Checking Phone Numbers...")
    res = requests.get("https://api.vapi.ai/phone-number", headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Failed to fetch numbers: {res.text}")
        return

    numbers = res.json()
    assistant_id = get_assistant_id("Office Manager Enterprise")
    
    found_number = None
    
    if not numbers:
        print("⚠️ No phone numbers found in your Vapi account.")
    else:
        import json
        with open("VAPI_NUMBERS_DUMP.json", "w") as f:
            json.dump(numbers, f, indent=2)
        print("✅ Dumped numbers to VAPI_NUMBERS_DUMP.json")

        for num in numbers:
            print(f"📞 Found Number: {num.get('number')} (Assigned to: {num.get('assistantId')})")
            if num.get('assistantId') == assistant_id:
                found_number = num.get('number')
                print(f"   ✅ MATCH! This number is assigned to Office Manager.")

    if found_number:
        print(f"\n🎉 Test Number: {found_number}")
    else:
        print(f"\n⚠️ No number assigned to Office Manager.")
        if not numbers:
             print("🛒 Buying a new phone number (Area Code 415)...")
             payload = {"areaCode": "415", "provider": "vapi", "number": ""} # Vapi provider usually gives test numbers or easy provisioning
             # Actually Vapi API allows buying via POST /phone-number
             try:
                 buy_res = requests.post("https://api.vapi.ai/phone-number", json={"provider": "vapi", "number": ""}, headers=HEADERS) # improved buy
                 if buy_res.status_code not in [200, 201]:
                      # Try twilio provider fallback or just generic buy
                      buy_res = requests.post("https://api.vapi.ai/phone-number", json={}, headers=HEADERS)
                 
                 if buy_res.status_code in [200, 201]:
                     new_num = buy_res.json()
                     print(f"✅ Purchased Number: {new_num.get('number')}")
                     
                     # Assign to Assistant
                     if assistant_id:
                         print(f"🔗 Assigning to Assistant {assistant_id}...")
                         update_res = requests.patch(f"https://api.vapi.ai/phone-number/{new_num.get('id')}", json={"assistantId": assistant_id}, headers=HEADERS)
                         if update_res.status_code == 200:
                             print(f"🎉 SUCCESS! Call this number to test: {new_num.get('number')}")
                         else:
                             print(f"❌ Failed to assign: {update_res.text}")
                 else:
                     print(f"❌ Failed to buy number: {buy_res.text}")
             except Exception as e:
                 print(f"❌ Error provisioning: {e}")
        else:
             # Assign existing free number
             first_num = numbers[0]
             print(f"🔗 Assigning existing number {first_num.get('number')} to Assistant...")
             update_res = requests.patch(f"https://api.vapi.ai/phone-number/{first_num.get('id')}", json={"assistantId": assistant_id}, headers=HEADERS)
             if update_res.status_code == 200:
                 print(f"🎉 SUCCESS! Call this number to test: {first_num.get('number')}")

if __name__ == "__main__":
    check_numbers()
