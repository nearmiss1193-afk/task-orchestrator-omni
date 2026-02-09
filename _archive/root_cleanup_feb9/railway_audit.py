
import asyncio
from playwright.async_api import async_playwright
import os

async def audit_railway():
    async with async_playwright() as p:
        # Launching with a visible browser so user can see if needed, 
        # but headless=True for background audit.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        project_id = "5b153983-325f-47dc-9f05-728795da226b"
        url = f"https://railway.app/project/{project_id}"
        
        print(f"🚀 Auditing Railway Project: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle")
            # Wait for content to load
            await asyncio.sleep(5)
            
            screenshot_path = os.path.abspath("railway_audit.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ Screenshot captured: {screenshot_path}")
            
            # Extract build logs or status if possible
            status = await page.inner_text("body")
            if "Active" in status or "Building" in status:
                print("📝 Found active/building status in dashboard.")
            
        except Exception as e:
            print(f"❌ Playwright Audit Failed: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(audit_railway())
