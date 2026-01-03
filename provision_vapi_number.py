import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_PRIVATE_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_assistant_id(name_fragment="Office Manager"):
    print(f"🔍 Searching for Assistant matching '{name_fragment}'...")
    res = requests.get("https://api.vapi.ai/assistant", headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Failed to list assistants: {res.text}")
        return None
    
    assistants = res.json()
    for a in assistants:
        if name_fragment in a.get("name", ""):
            print(f"✅ Found Assistant: {a.get('name')} ({a.get('id')})")
            return a.get("id")
    
    print("⚠️ No matching assistant found.")
    return None

def buy_number(assistant_id):
    print("🛒 Attempting to purchase new Vapi number...")
    
    # Try different payloads
    payloads = [
        {"provider": "vapi", "areaCode": "415"}, # San Francisco
        {"provider": "vapi", "areaCode": "307"}, # Wyoming
        {"provider": "vapi"} # Generic
    ]

    for payload in payloads:
        print(f"👉 Trying payload: {payload}")
        try:
            res = requests.post("https://api.vapi.ai/phone-number", json=payload, headers=HEADERS)
            if res.status_code in [200, 201]:
                data = res.json()
                new_number = data.get("number")
                number_id = data.get("id")
                print(f"✅ PURCHASE SUCCESSFUL! Number: {new_number} (ID: {number_id})")
                
                # Update with Assistant ID
                if assistant_id:
                    print(f"🔗 Linking to Assistant {assistant_id}...")
                    update_payload = {"assistantId": assistant_id}
                    update_res = requests.patch(f"https://api.vapi.ai/phone-number/{number_id}", json=update_payload, headers=HEADERS)
                    if update_res.status_code == 200:
                        print("✅ Link Successful!")
                    else:
                        print(f"⚠️ Link Failed: {update_res.text}")
                
                return new_number
            else:
                print(f"❌ Purchase Failed ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"❌ Error during purchase: {e}")
            
    return None

def main():
    assistant_id = get_assistant_id("Office Manager")
    if not assistant_id:
        # Fallback to hardcoded ID from previous context if search fails
        assistant_id = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"
        print(f"⚠️ Using fallback ID: {assistant_id}")

    new_number = buy_number(assistant_id)
    
    if new_number:
        print(f"\n📢 FINAL RESULT: {new_number}")
        # Save to file for easy reading
        with open("NEW_VAPI_NUMBER.txt", "w") as f:
            f.write(new_number)

if __name__ == "__main__":
    main()
