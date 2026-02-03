
import asyncio
import os
import time
from playwright.async_api import async_playwright

async def exorcise_ghost():
    user_data_dir = os.path.join(os.getcwd(), ".ghl_browser_data")
    print(f"[EXORCIST] Using data dir: {user_data_dir}")
    
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
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            page = await context.new_page()
            
            print(f"[EXORCIST] Navigating to {workflow_url}")
            await page.goto(workflow_url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(10) # Let it settle
            
            await page.screenshot(path=os.path.join(os.getcwd(), "ghl_initial.png"))
            
            # Check for frames
            print(f"[EXORCIST] Frames detected: {len(page.frames)}")
            for i, frame in enumerate(page.frames):
                print(f"  Frame {i}: {frame.url}")
            
            # Target the builder frame if it exists
            target = page
            for frame in page.frames:
                if "workflow" in frame.url.lower() and frame != page.main_frame:
                    target = frame
                    print(f"[EXORCIST] Switching to frame: {frame.url}")
                    break

            # 1. Trigger the Webhook Mapping
            print("[EXORCIST] Searching for Trigger node...")
            # Often nodes have text like "Trigger" or "Webhook"
            trigger = target.locator("text='Webhook', text='Trigger'").first
            if await trigger.count() > 0:
                await trigger.click()
                print("[EXORCIST] Trigger node clicked.")
                await asyncio.sleep(2)
                
                # Look for Fetch Sample
                fetch_btn = target.locator("button:has-text('Fetch Sample'), button:has-text('Test')").first
                if await fetch_btn.count() > 0:
                    await fetch_btn.click()
                    print("[EXORCIST] 'Fetch Sample' clicked.")
                    await asyncio.sleep(5)
                    await target.locator("button:has-text('Save Trigger'), button:has-text('Save')").first.click()
                else:
                    print("[EXORCIST] ⚠️ 'Fetch Sample' button not found in trigger sidebar.")
            else:
                print("[EXORCIST] ⚠️ Trigger node not found. Dumping nodes...")
                nodes = await target.locator(".hl-workflow-node, [role='button']").all_inner_texts()
                print(f"[EXORCIST] Found elements: {nodes[:10]}")

            # 2. Fix the SMS Action
            print("[EXORCIST] Searching for SMS action...")
            sms_node = target.locator("text='SMS', text='Send SMS'").first
            if await sms_node.count() > 0:
                await sms_node.click()
                print("[EXORCIST] SMS action node clicked.")
                await asyncio.sleep(2)
                
                # Use a very broad selector for the text area
                editor = target.locator(".ql-editor, textarea, [contenteditable='true']").first
                if await editor.count() > 0:
                    await editor.click()
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Backspace")
                    await page.keyboard.type("{{message}}")
                    print("[EXORCIST] {{message}} variable injected.")
                    
                    await target.locator("button:has-text('Save Action'), button:has-text('Save')").first.click()
                    print("[EXORCIST] Action saved.")
                else:
                    print("[EXORCIST] ❌ SMS editor not found.")
            else:
                print("[EXORCIST] ❌ SMS node NOT FOUND.")

            # 3. Final Save & Publish
            print("[EXORCIST] Saving and Publishing...")
            await page.locator("button:has-text('Save')").first.click()
            await asyncio.sleep(2)
            publish = page.locator("button:has-text('Publish'), button:has-text('Published')").first
            if await publish.count() > 0:
                await publish.click()
                print("[EXORCIST] 🎉 WORKFLOW PUBLISHED.")

            await page.screenshot(path=os.path.join(os.getcwd(), "ghl_final.png"))
            await context.close()
            print("[EXORCIST] FINISHED.")
            
        except Exception as e:
            print(f"[EXORCIST] ❌ FATAL: {str(e)}")
            await context.close()

if __name__ == "__main__":
    asyncio.run(exorcise_ghost())
