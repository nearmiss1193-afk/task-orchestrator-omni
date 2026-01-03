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
TARGET_NUMBER = "+18632132505"

SALES_PROMPT = """
You are Rachel, a **Senior Sales & Product Specialist** for **AI Service Co**.
**Mission:** Help business owners understand our AI automation tools and close deals.
**Tone:** Professional, Warm, Knowledgeable, Results-Oriented.
**Key Products:**
1. **Missed Call Text-Back:** "Never miss a lead again."
2. **AI Appointment Setter:** "Turn past customers into revenue."
3. **Unified Inbox:** "All your messages in one place."
**Pricing:**
- **Lite ($99/mo)**
- **Starter ($149/mo)**
- **Growth ($297/mo)** - Best Value
- **Pro ($497/mo)**
**Closing:**
- "Click 'Get Started' on the website."
- Or offer to take their name for a callback.
"""

FIRST_MESSAGE = "Thanks for calling AI Service Co. This is Rachel, your Sales Specialist. How can I help you automate your business today?"

def create_and_route():
    print("🚀 Creating NEW 'Empire Sales Specialist' Assistant...")
    
    # 1. Create Assistant
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "systemPrompt": SALES_PROMPT,
            "messages": [
                {
                    "content": SALES_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": FIRST_MESSAGE,
        "name": "Empire Sales Specialist",
        "voice": {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM" # Rachel
        }
    }
    
    res = requests.post("https://api.vapi.ai/assistant", headers=HEADERS, json=payload)
    if res.status_code != 201:
        print(f"❌ Creation Failed: {res.text}")
        return

    new_assistant = res.json()
    new_id = new_assistant.get('id')
    print(f"✅ Created Sales Assistant: {new_id}")
    
    # 2. Route Phone Number
    print(f"🔄 Re-routing {TARGET_NUMBER} to New Assistant {new_id}...")
    
    # Get Phone ID first
    p_res = requests.get("https://api.vapi.ai/phone-number", headers=HEADERS)
    phone_id = None
    for num in p_res.json():
        if num.get('number') == TARGET_NUMBER:
            phone_id = num.get('id')
            break
            
    if phone_id:
        patch_payload = { "assistantId": new_id }
        patch_res = requests.patch(f"https://api.vapi.ai/phone-number/{phone_id}", headers=HEADERS, json=patch_payload)
        if patch_res.status_code == 200:
            print("✅ SUCCESS: Phone Number Re-routed to Sales Specialist.")
        else:
             print(f"❌ Failed to Route: {patch_res.text}")
    else:
        print("❌ Phone Number ID NOT FOUND.")

if __name__ == "__main__":
    create_and_route()
