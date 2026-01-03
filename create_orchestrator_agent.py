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

# ORCHESTRATOR PROMPT
PROMPT_PATH = r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400\ORCHESTRATOR_PROMPT.md"
try:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        ORCHESTRATOR_SYSTEM_PROMPT = f.read()
except:
    # Fallback if artifact not readable
    ORCHESTRATOR_SYSTEM_PROMPT = "You are ANTIGRAVITY. Level 5 Orchestrator. You control the system."

def create_orchestrator():
    print(f"✨ Creating NEW Orchestrator Agent (Antigravity)...")
    
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-4-turbo",
            "systemPrompt": ORCHESTRATOR_SYSTEM_PROMPT,
            "messages": [
                {
                    "content": ORCHESTRATOR_SYSTEM_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": "Antigravity Online. Level 5 Connection Established.",
        "name": "Antigravity (Orchestrator)",
        "voice": {
             "provider": "11labs",
             "voiceId": "onwK4e9ZLuTAKqWW03F9" # Daniel
        }
    }
    
    try:
        res = requests.post(f"https://api.vapi.ai/assistant", headers=HEADERS, json=payload)
        res.raise_for_status()
        data = res.json()
        new_id = data.get('id')
        print(f"✅ SUCCESS: Created Orchestrator Agent.")
        print(f"🆔 NEW ASSISTANT ID: {new_id}")
        
        # Save to file so we can inject it
        with open("new_orchestrator_id.txt", "w") as f:
            f.write(new_id)
            
    except Exception as e:
        print(f"❌ FAILED to create assistant: {e}")
        if 'res' in locals():
            print(res.text)

if __name__ == "__main__":
    create_orchestrator()
