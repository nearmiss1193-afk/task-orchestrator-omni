import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
if not VAPI_PRIVATE_KEY:
    # Try to find it in the blitz script if not in env
    print("Warning: VAPI_PRIVATE_KEY not found in env, checking hardcoded values...")
    # For now, let's assume it's in .env or the blitz script has it. 
    # If this fails, I'll read blitz script for the key.

url = "https://api.vapi.ai/assistant"

headers = {
    "Authorization": f"Bearer {VAPI_PRIVATE_KEY}"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    assistants = response.json()
    
    print(f"Found {len(assistants)} assistants:")
    with open("vapi_assistants.json", "w") as f:
        json.dump(assistants, f, indent=2)
    print("Saved to vapi_assistants.json")
    
    for a in assistants:
        print(f"Name: {a.get('name', 'Unnamed')} | ID: {a.get('id')} | Type: {a.get('type', 'Unknown')}")
        
except Exception as e:
    print(f"Error listing assistants: {e}")
    if hasattr(e, 'response') and e.response:
        print(e.response.text)
