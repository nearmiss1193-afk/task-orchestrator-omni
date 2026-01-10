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
        "name": "System Reporter",
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "systemMessage": """
                    SECURITY PROTOCOL: RED.
                    1. On call start, say "Sovereign System. State your authorization code."
                    2. You MUST verify the code is "one one two nine seven five two nine nine zero" (1129752990).
                    3. If code is WRONG: Say "Access Denied" and hang up.
                    4. If code is CORRECT: Say "Access Granted. Command?" and enable tools (Status, Trigger Hunt).
                    5. Keep responses brief and military-style.
                    """,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_status",
                        "description": "Get system counting stats and health.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "check": {
                                    "type": "string",
                                    "description": "Confirmation",
                                    "enum": ["status"]
                                }
                            },
                            "required": ["check"]
                        }
                    },
                    "server": {
                        "url": "https://nearmiss1193-afk--empire-sovereign-v2-vapi-status.modal.run"
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "trigger_hunt",
                        "description": "Trigger the cloud prospector to find new leads immediately.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "confirm": {
                                    "type": "string",
                                    "description": "Confirmation to start",
                                    "enum": ["start"]
                                }
                            },
                            "required": ["confirm"]
                        }
                    },
                    "server": {
                        "url": "https://nearmiss1193-afk--empire-sovereign-v2-vapi-trigger-hunt.modal.run"
                    }
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
