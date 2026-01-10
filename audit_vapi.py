import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("VAPI_PRIVATE_KEY")

def list_agents():    # Get Office Manager Prompt
    print("\n--- FINDING OFFICE MANAGER ---")
    try:
        res2 = requests.get(
            "https://api.vapi.ai/assistant",
            headers={"Authorization": f"Bearer {KEY}"}
        )
        agents = res2.json()
        found = False
        for a in agents:
            if a.get('name') == "Office Manager":
                found = True
                print(f"ID: {a.get('id')}")
                print(f"PROMPT:\n{a.get('model', {}).get('systemPrompt')}\n")
        
        if not found:
            print("❌ Office Manager not found")
            
    except Exception as e:
        print(e)

if __name__ == "__main__":
    list_agents()
