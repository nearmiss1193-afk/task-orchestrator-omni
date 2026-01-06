import os
import time
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

class GHLBrowser:
    def __init__(self):
        self.email = os.getenv("GHL_EMAIL")
        self.password = os.getenv("GHL_PASSWORD")
        self.location_id = os.getenv("GHL_LOCATION_ID")
        self.user_data_dir = os.path.join(os.getcwd(), ".ghl_browser_data")

    async def login(self, page):
        print(f"[GHL] Navigating to login...")
        await page.goto("https://app.gohighlevel.com/", wait_until="networkidle")
        
        # Check if already logged in
        if "app.gohighlevel.com/v2/location" in page.url:
            print("[GHL] Already logged in.")
            return True

        print(f"[GHL] Attempting login for {self.email}...")
        await page.fill('input[name="email"]', self.email)
        await page.fill('input[name="password"]', self.password)
        await page.click('button[type="submit"]')
        
        # Check for 2FA or dashboard
        try:
            await page.wait_for_url("**/v2/location/**", timeout=15000)
            print("[GHL] Login successful.")
            return True
        except Exception as e:
            print(f"[GHL] Login failed or 2FA required: {e}")
            if "otp" in page.url or "verification" in page.url.lower():
                print("[GHL] 2FA DETECTED. Manual intervention required.")
            return False

    async def select_subaccount(self, page):
        target_url = f"https://app.gohighlevel.com/v2/location/{self.location_id}/dashboard"
        print(f"[GHL] Switching to location {self.location_id}...")
        await page.goto(target_url, wait_until="networkidle")
        if self.location_id in page.url:
            print("[GHL] Sub-account dashboard loaded.")
            return True
        return False

    async def send_sms(self, phone, message):
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=True,
                args=["--no-sandbox"]
            )
            page = await browser.new_page()
            
            if not await self.login(page):
                await browser.close()
                return False

            await self.select_subaccount(page)
            
            # Go to Contacts and find the phone number
            print(f"[GHL] Searching for contact: {phone}...")
            search_url = f"https://app.gohighlevel.com/v2/location/{self.location_id}/contacts/smart_list/all"
            await page.goto(search_url, wait_until="networkidle")
            
            await page.fill('input[placeholder="Search"]', phone)
            await page.press('input[placeholder="Search"]', 'Enter')
            await asyncio.sleep(3) # Wait for search results
            
            # Click on first contact
            contact_selector = "td.contact-name" 
            try:
                await page.click(contact_selector, timeout=5000)
                print("[GHL] Contact found and opened.")
            except:
                print("[GHL] Contact not found. Creating new contact...")
                # Logic for creating a contact if needed
                pass

            # Send SMS logic (interact with UI)
            # This is a stub for now, will refine selectors
            print("[GHL] SMS Logic Stub - Implement UI interaction here.")
            
            await browser.close()
            return True

if __name__ == "__main__":
    import sys
    ghl = GHLBrowser()
    if "--test-login" in sys.argv:
        asyncio.run(ghl.send_sms("test", "test"))
