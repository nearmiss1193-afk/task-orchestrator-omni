
import asyncio
import os
import time
from playwright.async_api import async_playwright

async def run_exorcist_v3():
    user_data_dir = os.path.join(os.getcwd(), ".ghl_browser_data")
    print(f"[EXORCIST-V3] Using data dir: {user_data_dir}")
    
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
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process"
                ]
            )
            page = await context.new_page()
            
            print(f"[EXORCIST-V3] Navigating to Workflow... (120s)")
            await page.goto(workflow_url, wait_until="load", timeout=120000)
            
            # PATIENCE ENGINE: Wait for the app to actually boot
            print("[EXORCIST-V3] Waiting for SPA bootstrap...")
            await asyncio.sleep(45) 
            
            # CLEAR MODALS (Blue popups)
            while True:
                modal_close = page.locator("button:has-text('Close'), button:has-text('Dismiss'), .hl-modal-close").first
                if await modal_close.is_visible():
                    await modal_close.click()
                    print("[EXORCIST-V3] Modal cleared.")
                    await asyncio.sleep(1)
                else:
                    break

            # FRAME LOCATOR STRIKE
            # Target the builder frame. It often has id='workflow-builder' or src containing 'builder'
            builder = page.frame_locator("#workflow-builder, iframe[src*='builder'], iframe[src*='workflow']").first
            
            # 1. TRIGGER MAPPING
            print("[EXORCIST-V3] Targeting Trigger Node [trigger-0]...")
            # Nodes often have data-node-id or are identifyable by text
            trigger = builder.locator("[data-node-id='trigger-0'], .hl-workflow-node").first
            await trigger.click(timeout=30000)
            print("[EXORCIST-V3] Trigger selected.")
            await asyncio.sleep(3)
            
            # Fetch Sample
            fetch = builder.locator("button:has-text('Fetch Sample'), button:has-text('Test')").first
            if await fetch.count() > 0:
                await fetch.click()
                print("[EXORCIST-V3] 'Fetch Sample' clicked.")
                await asyncio.sleep(10) # Heavy wait for webhook delivery
                
                # Check for "Select a sample"
                latest_sample = builder.locator(".sample-item, .sample-list-item").first
                if await latest_sample.count() > 0:
                    await latest_sample.click()
                    print("[EXORCIST-V3] Latest sample selected.")
                
                await builder.locator("button:has-text('Save Trigger')").first.click()
                print("[EXORCIST-V3] Trigger saved.")
            
            # 2. SMS ACTION MAPPING
            print("[EXORCIST-V3] Targeting SMS Action Node...")
            # Look for the SMS node
            sms_node = builder.locator(".hl-workflow-node:has-text('SMS'), [data-node-id*='sms'], [data-node-id*='action']").first
            await sms_node.click()
            print("[EXORCIST-V3] SMS node selected.")
            await asyncio.sleep(3)
            
            # Inject variable {{message}}
            print("[EXORCIST-V3] Injecting {{message}} into editor...")
            editor = builder.locator(".ql-editor, textarea, .sms-message-textarea").first
            await editor.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            # We use typing to simulate human input for the variable recognition
            await page.keyboard.type("{{message}}")
            await asyncio.sleep(1)
            
            await builder.locator("button:has-text('Save Action')").first.click()
            print("[EXORCIST-V3] SMS Action saved.")
            
            # 3. GLOBAL SAVE & PUBLISH
            # These are usually on the top-level PAGE, not the frame
            print("[EXORCIST-V3] Saving Workflow (Global)...")
            await page.locator("button:has-text('Save'), #save-workflow-btn").first.click()
            await asyncio.sleep(5)
            
            print("[EXORCIST-V3] Publishing Workflow (Global)...")
            # Find the publish toggle or button
            publish = page.locator("button:has-text('Publish'), #publish-workflow-btn").first
            if await publish.count() > 0:
                await publish.click()
                print("[EXORCIST-V3] 🎉 WORKFLOW PUBLISHED.")
            
            await page.screenshot(path="ghl_v3_final.png")
            print("[EXORCIST-V3] 🏁 MISSION COMPLETE. GHOST ANNIHILATED.")
            
            await context.close()
        except Exception as e:
            print(f"[EXORCIST-V3] ❌ STRIKE FAILED: {str(e)}")
            try:
                await page.screenshot(path="ghl_v3_error.png")
            except:
                pass
            await context.close()

if __name__ == "__main__":
    asyncio.run(run_exorcist_v3())
