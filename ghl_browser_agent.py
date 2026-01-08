"""
GHL Browser Agent (Sarah's Partner)
====================================
Uses Playwright to control GHL directly since API is not available.
Handles SMS and email sending through the GHL UI.

CAPABILITIES:
- Login to GHL with saved session
- Send SMS to contacts
- Send emails to contacts
- Search for contacts
- Add tags to contacts
- Trigger workflows

USAGE:
    agent = GHLBrowserAgent()
    await agent.login()
    await agent.send_sms("+13529368152", "Hey! This is Sarah...")
    await agent.close()
"""
import os
import asyncio
from playwright.async_api import async_playwright, Browser, Page
from dotenv import load_dotenv

load_dotenv()

GHL_EMAIL = os.getenv('GHL_EMAIL')
GHL_PASSWORD = os.getenv('GHL_PASSWORD')
GHL_LOCATION_ID = os.getenv('GHL_LOCATION_ID')

# Session storage path for persistent login
SESSION_PATH = os.path.join(os.path.dirname(__file__), '.ghl_session')


class GHLBrowserAgent:
    """Sarah's partner for browser-based GHL automation"""
    
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.logged_in = False
    
    async def start(self, headless: bool = True):
        """Start the browser with persistent session"""
        self.playwright = await async_playwright().start()
        
        # Use persistent context for session storage
        self.browser = await self.playwright.chromium.launch_persistent_context(
            SESSION_PATH,
            headless=headless,
            viewport={'width': 1280, 'height': 800}
        )
        
        # Get or create page
        if self.browser.pages:
            self.page = self.browser.pages[0]
        else:
            self.page = await self.browser.new_page()
    
    async def login(self, force: bool = False):
        """Login to GHL (skips if session is valid)"""
        if not self.page:
            await self.start()
        
        # Check if already logged in
        await self.page.goto('https://app.gohighlevel.com/v2/location/' + GHL_LOCATION_ID + '/dashboard')
        await self.page.wait_for_timeout(2000)
        
        # If we see the dashboard, we're logged in
        if '/dashboard' in self.page.url and 'login' not in self.page.url:
            print("✅ Already logged into GHL")
            self.logged_in = True
            return True
        
        # Need to login
        print("🔑 Logging into GHL...")
        await self.page.goto('https://app.gohighlevel.com/login')
        await self.page.wait_for_load_state('networkidle')
        
        # Fill credentials
        await self.page.fill('input[type="email"]', GHL_EMAIL)
        await self.page.fill('input[type="password"]', GHL_PASSWORD)
        await self.page.click('button[type="submit"]')
        
        # Wait for redirect
        await self.page.wait_for_timeout(5000)
        
        if 'dashboard' in self.page.url or 'location' in self.page.url:
            print("✅ GHL login successful")
            self.logged_in = True
            return True
        else:
            print(f"❌ Login may have failed. Current URL: {self.page.url}")
            return False
    
    async def search_contact(self, phone: str = None, email: str = None) -> str:
        """Search for a contact and return their ID or URL"""
        if not self.logged_in:
            await self.login()
        
        # Go to contacts page
        contacts_url = f'https://app.gohighlevel.com/v2/location/{GHL_LOCATION_ID}/contacts/smart_list/All'
        await self.page.goto(contacts_url)
        await self.page.wait_for_load_state('networkidle')
        
        # Search for contact
        search_term = phone or email
        search_input = await self.page.query_selector('input[placeholder*="Search"]')
        if search_input:
            await search_input.fill(search_term)
            await self.page.wait_for_timeout(2000)
        
        # Click first result if found
        first_contact = await self.page.query_selector('.contact-row, [data-testid="contact-row"]')
        if first_contact:
            await first_contact.click()
            await self.page.wait_for_timeout(1000)
            return self.page.url
        
        return None
    
    async def send_sms(self, phone: str, message: str) -> bool:
        """Send SMS to a contact via GHL UI"""
        if not self.logged_in:
            await self.login()
        
        # Search for contact first
        contact_url = await self.search_contact(phone=phone)
        
        if not contact_url:
            print(f"⚠️ Contact not found for {phone}, creating...")
            # Navigate to create contact
            await self.page.goto(f'https://app.gohighlevel.com/v2/location/{GHL_LOCATION_ID}/contacts/new')
            await self.page.wait_for_load_state('networkidle')
            
            # Fill phone
            phone_input = await self.page.query_selector('input[name="phone"], input[placeholder*="Phone"]')
            if phone_input:
                await phone_input.fill(phone)
            
            # Save contact
            save_btn = await self.page.query_selector('button:has-text("Save")')
            if save_btn:
                await save_btn.click()
                await self.page.wait_for_timeout(2000)
        
        # Now find and click SMS tab/button
        sms_tab = await self.page.query_selector('[data-testid="sms-tab"], button:has-text("SMS"), .sms-button')
        if sms_tab:
            await sms_tab.click()
            await self.page.wait_for_timeout(500)
        
        # Type message
        message_input = await self.page.query_selector('textarea[placeholder*="message"], textarea[placeholder*="SMS"], .message-input textarea')
        if message_input:
            await message_input.fill(message)
            
            # Send
            send_btn = await self.page.query_selector('button:has-text("Send"), button[aria-label="Send"]')
            if send_btn:
                await send_btn.click()
                print(f"✅ SMS sent to {phone} via GHL UI")
                return True
        
        print(f"❌ Could not send SMS to {phone}")
        return False
    
    async def send_email(self, email: str, subject: str, body: str) -> bool:
        """Send email to a contact via GHL UI"""
        if not self.logged_in:
            await self.login()
        
        # Search for contact
        contact_url = await self.search_contact(email=email)
        
        if not contact_url:
            print(f"⚠️ Contact not found for {email}")
            return False
        
        # Click email tab
        email_tab = await self.page.query_selector('[data-testid="email-tab"], button:has-text("Email")')
        if email_tab:
            await email_tab.click()
            await self.page.wait_for_timeout(500)
        
        # Fill subject and body
        subject_input = await self.page.query_selector('input[placeholder*="Subject"]')
        if subject_input:
            await subject_input.fill(subject)
        
        body_input = await self.page.query_selector('.email-body, .ql-editor, textarea')
        if body_input:
            await body_input.fill(body)
            
            # Send
            send_btn = await self.page.query_selector('button:has-text("Send")')
            if send_btn:
                await send_btn.click()
                print(f"✅ Email sent to {email} via GHL UI")
                return True
        
        print(f"❌ Could not send email to {email}")
        return False
    
    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()


async def test_agent():
    """Test the GHL Browser Agent"""
    agent = GHLBrowserAgent()
    
    try:
        await agent.start(headless=False)  # Visible for testing
        logged_in = await agent.login()
        
        if logged_in:
            print("\n--- Testing SMS ---")
            test_phone = os.getenv('TEST_PHONE')
            await agent.send_sms(test_phone, "Test from GHL Browser Agent - Sarah's partner!")
        
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(test_agent())
