
import asyncio
import os
from playwright.async_api import async_playwright

async def probe_session():
    user_data_dir = os.path.join(os.getcwd(), ".ghl_browser_data")
    print(f"[PROBE] Using data dir: {user_data_dir}")
    
    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = await context.new_page()
            
            target_url = "https://app.gohighlevel.com/v2/location/RnK4OjX0oDcqtWw0VyLr/dashboard"
            print(f"[PROBE] Navigating to {target_url}...")
            
            await page.goto(target_url, wait_until="networkidle", timeout=30000)
            
            current_url = page.url
            print(f"[PROBE] Final URL: {current_url}")
            
            if "login" in current_url.lower():
                print("RESULT: SESSION_EXPIRED")
            elif "location" in current_url.lower():
                print("RESULT: SESSION_ACTIVE")
                # Take a screenshot to verify state (optional but helpful)
                await page.screenshot(path="ghl_probe.png")
            else:
                print(f"RESULT: UNKNOWN ({current_url})")
                
            await context.close()
        except Exception as e:
            print(f"RESULT: ERROR ({str(e)})")

if __name__ == "__main__":
    asyncio.run(probe_session())
