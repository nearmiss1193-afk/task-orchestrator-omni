import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
TRANSFER_NUMBER = "+13529368152"

# IDs
JOHN_ID = "78b4c14a-4db3-4416-9289-d1bfd2409606"
SARAH_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

def add_transfer_tool(assistant_id, name):
    print(f"Adding Transfer Tool to {name} ({assistant_id})...")
    
    # 1. Fetch current config to respect existing tools (if any)
    # We want to patch the 'model' to include the tool
    
    tool_def = {
        "type": "transferCall",
        "destinations": [
            {
                "type": "number",
                "number": TRANSFER_NUMBER,
                "message": "Transferring you to a specialist now. Please hold."
            }
        ],
        "function": {
            "name": "transferCall",
            "description": "Use this tool ONLY when the user explicitly asks to speak to a real person, a human, or a manager. Do not use for general questions.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "server": {
            "url": "https://api.vapi.ai/tool/transferCall" # Standard Vapi endpoint or internal
        }
    }
    
    # Actually, Vapi's structure for 'transferCall' is a specific tool type.
    # We should append it to the `model.tools` list.
    
    # Fetch current
    res = requests.get(f"https://api.vapi.ai/assistant/{assistant_id}", headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch {name}: {res.text}")
        return

    current_config = res.json()
    model_config = current_config.get("model", {})
    existing_tools = model_config.get("tools", [])
    
    # Remove existing transfer tools if any to avoid dupes
    new_tools = [t for t in existing_tools if t.get("type") != "transferCall"]
    new_tools.append(tool_def)
    
    patch_payload = {
        "model": {
            **model_config,
            "tools": new_tools
        }
    }
    
    patch_res = requests.patch(f"https://api.vapi.ai/assistant/{assistant_id}", headers=headers, json=patch_payload)
    
    if patch_res.status_code == 200:
        print(f"SUCCESS: {name} can now transfer to {TRANSFER_NUMBER}")
    else:
        print(f"ERROR patching {name}: {patch_res.text}")

if __name__ == "__main__":
    add_transfer_tool(JOHN_ID, "John (Roofing)")
    add_transfer_tool(SARAH_ID, "Sarah (HVAC)")
