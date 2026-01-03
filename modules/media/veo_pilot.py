
import os
import time
import random
from playwright.sync_api import sync_playwright

# SCENES CONFIGURATION
SCENES = [
    {
        "name": "Scene 1: The Pain",
        "prompt": "Cinematic, photorealistic handheld video of a sweaty HVAC contractor working in a dark, tight attic with pink insulation. He is holding a flashlight and looking stressed. High quality, 4k.",
        "type": "video"
    },
    {
        "name": "Scene 2: The Solution",
        "prompt": "SKIP - USING STATIC ASSET", 
        "type": "image"
    },
    {
        "name": "Scene 3: The Result",
        "prompt": "A confident, happy HVAC technician in a clean uniform standing outside a white service van in bright sunlight. He is looking at his smartphone and smiling. Blue sky background.",
        "type": "video"
    }
]

def run_veo_pilot():
    print("🚀 Veo Pilot: Initializing...")
    
    # Path to persist login cookies
    user_data_dir = os.path.join(os.getcwd(), ".veo_browser_data")
    os.makedirs(user_data_dir, exist_ok=True)

    with sync_playwright() as p:
        # Launch persistent context to save login state
        print(f"📂 Loading User Profile: {user_data_dir}")
        executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            executable_path=executable_path, # Use REAL Chrome
            args=["--start-maximized"],
            channel="chrome" 
        )
        
        page = browser.pages[0]
        
        # TARGET URL (Assumption: VideoFX or Google Vids)
        # Replacing with generic VideoFX url. 
        # User can redirect if needed.
        target_url = "https://aitestkitchen.withgoogle.com/tools/video-fx"
        print(f"🌐 Navigating to: {target_url}")
        page.goto(target_url)
        
        # 1. LOGIN GATE
        print("🔒 Waiting for user to ensure Login...")
        # Check for common login indicators or just wait
        try:
            page.wait_for_selector("textarea, input[type='text']", timeout=10000)
            print("✅ Detected input field! Assuming logged in.")
        except:
            print("⚠️ Login required or Interface loading...")
            print("👉 ACTION REQUIRED: Please Log In manually in the browser window.")
            print("👉 Press ENTER in this terminal once you are on the Create screen.")
            input("Waiting for confirmation...")

        # 2. GENERATION LOOP
        for scene in SCENES:
            if scene["type"] != "video":
                print(f"⏩ {scene['name']}: Skipping (Static/Other)")
                continue
                
            print(f"🎬 Processing {scene['name']}...")
            prompt = scene["prompt"]
            
            # Find Input
            # Heuristic: The largest textarea is usually the prompt box
            textareas = page.query_selector_all("textarea")
            if not textareas:
                print("❌ Could not find prompt input. Please focus it manually.")
                input("Press ENTER after clicking the text box...")
                textareas = page.query_selector_all("textarea")
            
            # Type Prompt
            box = textareas[0] 
            box.fill("")
            box.type(prompt, delay=50) # Type like a human
            print(f"✍️ Typed prompt: {prompt[:30]}...")
            
            # Find Generate Button
            # Look for button with text "Generate"
            print("🖱️ Looking for 'Generate' button...")
            try:
                # Try specific selectors or text
                page.get_by_text("Generate", exact=False).click()
            except:
                print("❌ Auto-click failed. Please Click Generate Manually.")
            
            # Wait for Generation
            print("⏳ Waiting for generation (estimated 30-60s)...")
            # We can't easily detect 'done' without specific selectors.
            # We will wait for a fix time then ask user to save.
            time.sleep(30) 
            
            print(f"✅ {scene['name']} should be ready.")
            print("👉 ACTION: Please Download the video manually if auto-download is not set.")
            input("Press ENTER to proceed to next scene...")
            
        print("🏁 All Scenes Processed.")
        print("💾 Closing Session...")
        browser.close()

if __name__ == "__main__":
    run_veo_pilot()
