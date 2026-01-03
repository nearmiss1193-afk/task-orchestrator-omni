
import requests
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("VAPI_PRIVATE_KEY")

if not API_KEY:
    print("❌ VAPI_PRIVATE_KEY missing.")
    exit(1)

def get_ngrok_url():
    try:
        with open("ngrok.log", "r") as f:
            content = f.read()
            # Regex to find https URL
            match = re.search(r"url=(https://[a-zA-Z0-9-]+\.ngrok-free\.app)", content)
            if not match:
                 # Try .dev or .io just in case
                 match = re.search(r"url=(https://[a-zA-Z0-9-]+\.ngrok-free\.dev)", content)
            
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error reading ngrok log: {e}")
    return None

def main():
    print("🚀 Starting Vapi Voice Intelligence Upgrade...")
    
    # 1. Get Tunnel URL
    base_url = get_ngrok_url()
    if not base_url:
        print("❌ Could not find Ngrok URL in logs. Is ngrok running?")
        # Fallback or Exit?
        # Let's try to query localhost:4040 if log failed
        try:
            r = requests.get("http://localhost:4040/api/tunnels")
            base_url = r.json()['tunnels'][0]['public_url']
            print("✅ Found URL via API: " + base_url)
        except:
             print("❌ Failed to find Tunnel URL.")
             return

    server_url = f"{base_url}/api/vapi/webhook"
    print(f"🔗 Server URL: {server_url}")

    # 2. Load Persona (System Prompt)
    try:
        with open("OFFICE_MANAGER_PROMPT.md", "r") as f:
            system_prompt = f.read()
    except:
        print("❌ OFFICE_MANAGER_PROMPT.md not found.")
        return

    # 3. Load Tools
    try:
        with open("vapi_tools_config.json", "r") as f:
            tools = json.load(f)
    except:
        print("❌ vapi_tools_config.json not found.")
        return

    # 4. Attach Server URL to Tools & Assistant
    for tool in tools:
        if tool.get("type") == "function":
            tool["function"]["serverUrl"] = server_url
            print(f"   - Tool Configured: {tool['function']['name']}")

    # 5. Build Payload
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "systemPrompt": system_prompt,
            "tools": tools
        },
        "serverUrl": server_url
    }

    # 6. Find & Update
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    # Get ID
    target_id = None
    try:
        with open("vapi_id.txt", "r") as f:
            target_id = f.read().strip()
    except:
        print("⚠️ vapi_id.txt not found. Searching by name...")
        res = requests.get("https://api.vapi.ai/assistant", headers=headers)
        for a in res.json():
            if a.get("name") == "Office Manager Enterprise":
                target_id = a.get("id")
                break
    
    if not target_id:
        print("❌ Could not find assistant ID.")
        return

    print(f"🔄 Updating Assistant {target_id}...")
    resp = requests.patch(f"https://api.vapi.ai/assistant/{target_id}", json=payload, headers=headers)
    
    if resp.status_code == 200:
        print("✅ UPGRADE COMPLETE!")
        print("The Office Manager is now ONLINE and INTELLIGENT.")
    else:
        print(f"❌ Update Failed: {resp.text}")

if __name__ == "__main__":
    main()
