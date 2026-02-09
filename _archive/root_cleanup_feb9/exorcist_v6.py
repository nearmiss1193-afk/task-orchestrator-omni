
import asyncio
import os
import shutil
import time
import requests
from playwright.async_api import async_playwright

async def run_exorcist_v6():
    # 1. THE WARM STRIKE
    webhook_url = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/44e67279-2ad5-491c-82f0-f8eaadea085c"
    print(f"[EXORCIST-V6] Warm Strike to ensure fresh sample...")
    try:
        requests.post(webhook_url, json={"phone": "+1234567890", "message": "GHOST_EXORCISM_FINAL_STRIKE_DATA"}, timeout=5)
    except: pass

    # 2. PROFILE HIJACK
    primary_profile_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    target_data_dir = os.path.join(os.getcwd(), ".ghl_strike_v6")
    
    try:
        if os.path.exists(target_data_dir): shutil.rmtree(target_data_dir)
        os.makedirs(target_data_dir, exist_ok=True)
        default_profile = os.path.join(primary_profile_path, "Default")
        if os.path.exists(default_profile):
            target_default = os.path.join(target_data_dir, "Default")
            os.makedirs(target_default, exist_ok=True)
            for f in ["Cookies", "Local Storage", "Session Storage"]:
                src = os.path.join(default_profile, f)
                dst = os.path.join(target_default, f)
                if os.path.exists(src):
                    try: shutil.copytree(src, dst, dirs_exist_ok=True) if os.path.isdir(src) else shutil.copy2(src, dst)
                    except: pass
    except: pass

    location_id = "RnK4OjX0oDcqtWw0VyLr"
    workflow_id = "44e67279-2ad5-491c-82f0-f8eaadea085c"
    
    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                target_data_dir,
                headless=True,
                viewport={"width": 1920, "height": 1080},
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-web-security"]
            )
            page = await context.new_page()
            
            # 1. LAND ON LOCATION SWITCHER
            print("[EXORCIST-V6] Navigating to Switcher...")
            await page.goto("https://app.gohighlevel.com/v2/location", wait_until="load", timeout=90000)
            await asyncio.sleep(20) # Significant wait for switcher to load
            
            # Find and click the sub-account
            print(f"[EXORCIST-V6] Searching for Account: {location_id}")
            # Try to find a link with the location ID
            account_link = page.locator(f"a[href*='{location_id}'], [data-id*='{location_id}']").first
            if await account_link.count() > 0:
                await account_link.click(force=True)
                print("[EXORCIST-V6] Account selected.")
            else:
                print(f"[EXORCIST-V6] ⚠️ Account link not found. Attempting direct nav to workflow...")
                
            # 2. DIRECT NAV TO WORKFLOW (Fallback/Primary)
            workflow_url = f"https://app.gohighlevel.com/v2/location/{location_id}/automation/workflow/{workflow_id}"
            await page.goto(workflow_url, wait_until="load", timeout=90000)
            await asyncio.sleep(45) # PATIENCE ENGINE
            
            # CLEAR OVERLAYS
            await page.evaluate("""() => {
                document.querySelectorAll('button:has-text("Close"), .hl-modal-close, .introjs-overlay, .pendo-guide-container').forEach(el => el.click());
            }""")

            # 3. SELECTOR SURGERY (Frame & Shadow DOM)
            builder = page.frame_locator("#workflow-builder, iframe[src*='builder']").first
            
            # Trigger Strike
            trigger = builder.locator("[data-node-id='trigger-0'], .hl-workflow-node").first
            await trigger.click(force=True)
            await asyncio.sleep(5)
            
            fetch = builder.locator("button:has-text('Fetch Sample'), button:has-text('Test')").first
            if await fetch.count() > 0:
                await fetch.click(force=True)
                await asyncio.sleep(10)
                # Select latest sample
                await builder.locator(".sample-item").first.click(force=True)
                await builder.locator("button:has-text('Save Trigger')").first.click(force=True)
                print("[EXORCIST-V6] Trigger updated.")

            # SMS Strike
            sms = builder.locator(".hl-workflow-node:has-text('SMS'), [data-node-id*='sms']").first
            await sms.click(force=True)
            await asyncio.sleep(5)
            
            editor = builder.locator(".ql-editor, textarea, .sms-message-textarea").first
            await editor.click(force=True)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.keyboard.type("{{message}}")
            await builder.locator("button:has-text('Save Action')").first.click(force=True)
            print("[EXORCIST-V6] SMS updated.")

            # 4. NUCLEAR GLOBAL SAVE
            print("[EXORCIST-V6] Nuclear Global Save & Publish...")
            await page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button'));
                btns.find(b => b.textContent.toLowerCase().trim() === 'save')?.click();
                setTimeout(() => {
                    btns.find(b => b.textContent.toLowerCase().includes('publish'))?.click();
                }, 3000);
            }""")
            await asyncio.sleep(10)
            
            await page.screenshot(path="ghl_v6_final.png")
            print("[EXORCIST-V6] 🎉 GHOST ANNIHILATED. STRIKE COMPLETE.")
            await context.close()
        except Exception as e:
            print(f"[EXORCIST-V6] ❌ FATAL ERROR: {e}")
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_exorcist_v6())
