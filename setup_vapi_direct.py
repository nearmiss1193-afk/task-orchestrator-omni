
import requests
import json
import os

# Configuration
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("VAPI_PRIVATE_KEY")
SERVER_URL = "https://nearmiss1193-afk--ghl-omni-automation-office-voice-tool.modal.run"
TOOL_CONFIG_PATH = "vapi_tools_config.json"

if not API_KEY:
    print("❌ Error: VAPI_PRIVATE_KEY not found in environment.")
    exit(1)

def main():
    print(f"🚀 Configuring Vapi Assistant using Direct API...")
    
    # 1. Load Tools
    if not os.path.exists(TOOL_CONFIG_PATH):
        print(f"❌ Error: {TOOL_CONFIG_PATH} not found.")
        return

    with open(TOOL_CONFIG_PATH, "r") as f:
        tools = json.load(f)

    # 2. Attach Server URL to Tools
    for tool in tools:
        if tool.get("type") == "function":
            tool["function"]["serverUrl"] = SERVER_URL
            print(f"   - Attached Server URL to tool: {tool['function']['name']}")

    # 3. Define Assistant Payload
    assistant_payload = {
        "name": "Office Manager Enterprise",
        "voice": {
            "provider": "11labs", 
            "voiceId": "21m00Tcm4TlvDq8ikWAM" # Standard 'Rachel'
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "systemPrompt": """You are the Office Manager Orchestrator.
Your goal is to manage inventory and task assignment for the business.

SECURITY PROTOCOL:
1. Before executing ANY task (adding a task or updating inventory), you MUST repeat the request back to the user.
2. Demand a confirmation number.
3. If the user provided code "11752990", you are authorized to proceed. execute the tool.
4. If the code is incorrect or missing, DENY the request and ask for the code.

LATENCY MASKING PROTOCOL (V50.0):
- INTERJECTION: As soon as the user finishes a sentence, using your "Active Listening" layer, insert a verbal nod ("Mm-hmm", "Got it", "Okay", "Checking") IMMEDIATELY.
- DO NOT wait for the full heavy logic to process before saying this.
- This reduces perceived latency from 800ms to 200ms.

Example:
User: "Do you have a technician for tomorrow?"
You: "Mm-hmm... I received a request to order 500 units of paper. Please provide the confirmation number."
User: "11752990"
You: "Got it... Authorization confirmed."

Be professional and strict with this protocol.""",
            "tools": tools
        },
        "transcriber": {
            "provider": "deepgram"
        },
        "serverUrl": SERVER_URL
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 4. Check for Existing Assistant to Update
    print("🔍 Checking existing assistants...")
    try:
        res = requests.get("https://api.vapi.ai/assistant", headers=headers)
        res.raise_for_status()
        assistants = res.json()
    except Exception as e:
        print(f"❌ Failed to list assistants: {e}")
        return

    target_id = None
    for a in assistants:
        if a.get("name") == "Office Manager Enterprise":
            target_id = a.get("id")
            break

    # 5. Create or Update
    if target_id:
        print(f"🔄 Found existing assistant (ID: {target_id}). Updating...")
        resp = requests.patch(f"https://api.vapi.ai/assistant/{target_id}", json=assistant_payload, headers=headers)
    else:
        print(f"✨ Creating NEW assistant 'Office Manager Enterprise'...")
        resp = requests.post("https://api.vapi.ai/assistant", json=assistant_payload, headers=headers)

    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"✅ SUCCESS! Assistant Configured.")
        print(f"👉 ID: {data.get('id')}")
        print(f"👉 Voice: {data.get('voice', {}).get('voiceId')}")
        print(f"👉 Server: {data.get('serverUrl')}")
        with open("vapi_id.txt", "w") as f:
            f.write(data.get('id'))

    else:
        print(f"❌ Failed: {resp.status_code}")
        with open("vapi_error.json", "w") as f:
            f.write(resp.text)
        print("See vapi_error.json for details.")

if __name__ == "__main__":
    main()
