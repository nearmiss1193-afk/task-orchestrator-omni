
import asyncio
from playwright.async_api import async_playwright
import json
import requests
import os
import time

TOOL_CONFIG_PATH = "vapi_tools_config.json"
SERVER_URL = "https://nearmiss1193-afk--ghl-omni-automation-office-voice-tool.modal.run"

def get_tool_config():
    with open(TOOL_CONFIG_PATH, "r") as f:
        return json.load(f)

async def main():
    print("🚀 Launching Vapi Dashboard for Authorization...")
    
    async with async_playwright() as p:
        # Use SYSTEM CHROME PROFILE (Match setup_products.py pattern)
        user_home = os.path.expanduser("~")
        system_profile_path = os.path.join(user_home, "AppData", "Local", "Google", "Chrome", "User Data")
        
        executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(executable_path):
             executable_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

        if os.path.exists(system_profile_path):
            print(f"📂 Connecting to System Profile: {system_profile_path}")
            user_data_dir = system_profile_path
        else:
            print("⚠️ System profile not found. Falling back to local.")
            user_data_dir = os.path.join(os.getcwd(), ".ghl_browser_data")

        print("⚠️ IF THIS FAILS: Please manually close ALL Chrome windows and retry.")
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            executable_path=executable_path,
            channel="chrome", 
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
            viewport=None
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        await page.goto("https://dashboard.vapi.ai/assistants")
        
        print("\n👉 ACTION REQUIRED: Please Log In to Vapi in the browser window.")
        print("⏳ Waiting for you to log in and reach the Dashboard...")
        
        # Wait for a token to appear in localStorage or a specific API call
        # Vapi likely stores auth in localStorage as 'vapi-token' or similar, or cookies.
        # We will poll for it.
        
        # Monitor Network Traffic for Authorization Header
        api_token_future = asyncio.Future()
        
        # Monitor Network Traffic (Relaxed Filter)
        api_token_future = asyncio.Future()
        
        async def on_request(request):
            headers = request.headers
            auth = headers.get("authorization") or headers.get("Authorization")
            if auth and "Bearer eyJ" in auth: # JWT format check
                if not api_token_future.done():
                    print(f"✅ Detected Authorization Header on {request.url[:50]}...")
                    api_token_future.set_result(auth)

        page.on("request", on_request)
        
        print("⏳ Waiting for credentials (Network OR LocalStorage)...")
        print("👉 Please Log In or Refresh the page.")

        start_time = time.time()
        token = None
        
        while time.time() - start_time < 180: # 3 minute timeout
            # 1. Check Network Future
            if api_token_future.done():
                token_header = api_token_future.result()
                token = token_header.replace("Bearer ", "").strip()
                print("✅ Captured Token via Network!")
                break
            
            # 2. Check LocalStorage (Fallback)
            try:
                local_storage = await page.evaluate("() => JSON.stringify(localStorage)")
                store = json.loads(local_storage)
                for k, v in store.items():
                    # Look for JWT-like strings
                    if isinstance(v, str) and v.startswith("eyJ") and len(v) > 100:
                        # Verify against API
                        print(f"🕵️ Testing candidate key from localStorage: {k}...")
                        res = requests.get("https://api.vapi.ai/assistant", headers={"Authorization": f"Bearer {v}"})
                        if res.status_code == 200:
                            token = v
                            print(f"✅ Captured Token via LocalStorage!")
                            break
            except:
                pass
            
            if token:
                break
                
            await asyncio.sleep(2)

        if not token:
            print("❌ Timeout: Did not detect valid credentials.")
            # Keep browser open for user to debug
            await asyncio.sleep(10)
            return

        print(f"🔓 Authenticated. Token length: {len(token)}")
                
        print(f"🔓 Authenticated. Configuring 'Office Manager Enterprise'...")
        
        # 1. Define the Assistant Config
        tools = get_tool_config()
        
        # Attach the Server URL to each tool (Vapi requires it in the function definition or assistant level)
        # Actually Vapi API structure for tools:
        # "functions": [ { "name":..., "parameters":..., "serverUrl": ... } ]
        
        for tool in tools:
            if tool.get("type") == "function":
                tool["function"]["serverUrl"] = SERVER_URL
                
        assistant_payload = {
            "name": "Office Manager Enterprise",
            "voice": {
                "provider": "11labs", 
                "voiceId": "21m00Tcm4TlvDq8ikWAM" # Standard 'Rachel' or similar default
            },
            "model": {
                "model": "gpt-4o",
                "systemPrompt": "You are an efficient, professional Office Manager. Manage inventory and tasks. Be concise."
            },
            "transcriber": {
                "provider": "deepgram"
            },
            "tools": tools,
            "serverUrl": SERVER_URL # Fallback
        }
        
        # 2. Check if exists to Update vs Create
        # We already fetched list to validate token
        res = requests.get("https://api.vapi.ai/assistant", headers={"Authorization": f"Bearer {token}"})
        assistants = res.json()
        
        target_id = None
        for a in assistants:
            if a.get("name") == "Office Manager Enterprise":
                target_id = a.get("id")
                break
        
        if target_id:
            print(f"🔄 Updating existing assistant: {target_id}")
            resp = requests.patch(f"https://api.vapi.ai/assistant/{target_id}", json=assistant_payload, headers={"Authorization": f"Bearer {token}"})
        else:
            print(f"mw Creating NEW assistant...")
            resp = requests.post("https://api.vapi.ai/assistant", json=assistant_payload, headers={"Authorization": f"Bearer {token}"})
            
        if resp.status_code in [200, 201]:
            print(f"✅ SUCCESS! Office Manager Agent is Live.")
            print(f"👉 ID: {resp.json().get('id')}")
            print("You can close the browser now.")
        else:
            print(f"❌ Failed to configure: {resp.text}")
            
        await asyncio.sleep(5) 
        # await browser.close() # Keep open briefly for user to see

if __name__ == "__main__":
    asyncio.run(main())
