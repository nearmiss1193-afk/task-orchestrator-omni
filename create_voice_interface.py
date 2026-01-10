import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("VAPI_PRIVATE_KEY")
# New endpoint base URL (removes specific path so we append later)
SERVER_URL = "https://nearmiss1193-afk--empire-sovereign-v2"

def create_reporter():
    print("🎙️ Creating System Reporter Agent...")
    
    # Vapi Tool Schema (Server-Side)
    # Note: Vapi expects 'server' at the tool level, and strict 'function' schema.
    
    agent_payload = {
        "name": "System Reporter Minimal",
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "messages": [
                 {
                    "role": "system",
                    "content": "You are a helpful assistant." 
                 }
            ]
        },
        "voice": {
             "provider": "11labs",
             "voiceId": "flq6f7yk4Ece79KdVNzY"
        }
    }
    res = requests.post(
        "https://api.vapi.ai/assistant",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json=agent_payload
    )
    
    if res.status_code == 201:
        agent = res.json()
        print(f"✅ Created Agent: {agent['id']}")
        return agent['id']
    else:
        print(f"❌ Failed to create agent: {res.text}")
        return None

def buy_number(agent_id):
    if not agent_id: return
    
    print("📞 Purchasing Number...")
    # 1. Search for a number (Area code 415 or random)
    # Note: Vapi API requires finding a number first or auto-buying.
    # We will try to buy a generic one.
    
    buy_payload = {
        "assistantId": agent_id,
        "areaCode": "415" # Tech/SF area code for "System"
    }
    
    res = requests.post(
        "https://api.vapi.ai/phone-number",
         headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
         json=buy_payload
    )
    
    if res.status_code == 201:
        phone = res.json()
        print(f"✅ NUMBER PURCHASED: {phone.get('number')}")
        print("Note: Call this number for updates.")
    else:
        print(f"⚠️ Could not buy number automatically: {res.text}")
        print(f"👉 Please go to Vapi Dashboard and assign a number to Agent ID: {agent_id}")

if __name__ == "__main__":
    aid = create_reporter()
    buy_number(aid)
