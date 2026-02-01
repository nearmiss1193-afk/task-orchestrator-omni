
import asyncio
import os
import time
from playwright.async_api import async_playwright

async def run_exorcist():
    # Attempt to use the actual Chrome profile if possible, fallback to local data
    profile_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    user_data_dir = os.path.join(os.getcwd(), ".ghl_browser_data")
    
    # We'll use the project-local one as it's less likely to be 'locked' by an open Chrome
    print(f"[EXORCIST] Using session profile: {user_data_dir}")
    
    workflow_id = "44e67279-2ad5-491c-82f0-f8eaadea085c"
    location_id = "RnK4OjX0oDcqtWw0VyLr"
    workflow_url = f"https://app.gohighlevel.com/v2/location/{location_id}/automation/workflow/{workflow_id}"
    
    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=True,
                viewport={"width": 1920, "height": 1080},
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security"
                ]
            )
            page = await context.new_page()
            
            print(f"[EXORCIST] Navigating to Workflow... (Timeout: 120s)")
            await page.goto(workflow_url, wait_until="load", timeout=120000)
            
            # PATIENCE ENGINE: Wait for the app to actually boot
            print("[EXORCIST] Waiting for SPA bootstrap...")
            for i in range(12): # Wait up to 60 more seconds
                await asyncio.sleep(5)
                content = await page.content()
                if "Initializing" not in content and "hl-workflow" in content.lower():
                    print(f"[EXORCIST] Bootstrap complete at {i*5}s.")
                    break
                print(f"  ...still loading ({i*5}s)")
            
            # CLEAR MODALS: Bypassing "Blue" popups, what's new, etc.
            print("[EXORCIST] Clearing potential modals...")
            close_buttons = ["button:has-text('Close')", "button:has-text('Dismiss')", ".hl-modal-close", ".close-icon"]
            for btn in close_buttons:
                if await page.locator(btn).is_visible():
                    await page.click(btn)
                    print(f"  Clicked close button: {btn}")

            # LOCATE BUILDER FRAME (Crucial for V2)
            target = page
            # GHL V2 sometimes uses an iframe for the builder
            frames = page.frames
            for f in frames:
                if "workflow" in f.url.lower() and f != page.main_frame:
                    target = f
                    print(f"[EXORCIST] Found Builder Frame: {f.url}")
                    break

            # 1. TRIGGER Webhook Strike
            print("[EXORCIST] Searching for Trigger Node...")
            trigger = target.locator("text='Trigger', text='Webhook'").first
            await trigger.click(timeout=30000)
            print("[EXORCIST] Trigger selected.")
            await asyncio.sleep(3)
            
            # Fetch Sample
            fetch = target.locator("button:has-text('Fetch Sample')").first
            if await fetch.count() > 0:
                await fetch.click()
                print("[EXORCIST] Fetch Sample triggered.")
                await asyncio.sleep(8) # Wait for sample delivery
                
                # Select latest sample if dropdown appears
                dropdown = target.locator(".select-sample-dropdown, .sample-dropdown").first
                if await dropdown.is_visible():
                    await dropdown.click()
                    await target.locator(".sample-item").first.click()
                    print("[EXORCIST] Newest sample selected.")
                
                await target.locator("button:has-text('Save Trigger')").first.click()
                print("[EXORCIST] Trigger saved.")
            
            # 2. SMS Action Mapping
            print("[EXORCIST] Searching for SMS Action Node...")
            sms = target.locator("text='SMS', text='Send SMS'").first
            await sms.click(timeout=20000)
            print("[EXORCIST] SMS node selected.")
            await asyncio.sleep(3)
            
            # Fill the editor
            editor = target.locator(".ql-editor, .sms-message-textarea, [contenteditable='true']").first
            await editor.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.keyboard.type("{{message}}")
            print("[EXORCIST] {{message}} variable injected.")
            
            await target.locator("button:has-text('Save Action')").first.click()
            print("[EXORCIST] Action saved.")
            
            # 3. GLOBAL SAVE & PUBLISH
            print("[EXORCIST] Finalizing Workflow...")
            await page.locator("button:has-text('Save')").first.click()
            await asyncio.sleep(3)
            
            # Click Publish (it's often a toggle or a button near Save)
            publish = page.locator("button:has-text('Publish'), #publish-workflow-btn").first
            if await publish.count() > 0:
                await publish.click()
                print("[EXORCIST] 🎉 WORKFLOW PUBLISHED.")
            
            print("[EXORCIST] 🏁 MISSION COMPLETE. GHOST EXORCISED.")
            await page.screenshot(path="ghl_strike_final.png")
            
            await context.close()
        except Exception as e:
            print(f"[EXORCIST] ❌ STRIKE FAILED: {str(e)}")
            try:
                await page.screenshot(path="ghl_strike_error.png")
            except:
                pass
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_exorcist())
