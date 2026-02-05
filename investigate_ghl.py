"""
GHL Investigation Script - Uses Playwright to investigate email status
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# GHL Credentials (from .env)
GHL_EMAIL = os.getenv("GHL_EMAIL", "nearmiss1193@gmail.com")
GHL_PASSWORD = os.getenv("GHL_PASSWORD", "Inez11752990@")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID", "RnK4OjX0oDcqtWw0VyLr")

async def investigate_ghl():
    """Investigate GHL email delivery and workflow status"""
    from playwright.async_api import async_playwright
    
    print("=" * 60)
    print("GHL INVESTIGATION")
    print("=" * 60)
    print(f"Email: {GHL_EMAIL}")
    print(f"Location ID: {GHL_LOCATION_ID}")
    print("-" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for debugging
        context = await browser.new_context()
        page = await context.new_page()
        
        # 1. Navigate to GHL Login
        print("\n📍 Step 1: Logging into GHL...")
        await page.goto("https://app.gohighlevel.com/", wait_until="networkidle")
        
        # Check if already logged in
        if "app.gohighlevel.com/v2/location" in page.url:
            print("✅ Already logged in!")
        else:
            # Fill login form
            print("📝 Filling login form...")
            try:
                await page.fill('input[name="email"]', GHL_EMAIL, timeout=5000)
                await page.fill('input[name="password"]', GHL_PASSWORD)
                await page.click('button[type="submit"]')
                
                # Wait for dashboard
                try:
                    await page.wait_for_url("**/v2/location/**", timeout=30000)
                    print("✅ Login successful!")
                except Exception as e:
                    print(f"⚠️ Login may require 2FA or failed: {e}")
                    # Check if 2FA
                    if "otp" in page.url.lower() or "verification" in page.url.lower():
                        print("🔐 2FA DETECTED - Manual intervention required")
                        print("⏳ Waiting 60 seconds for manual 2FA...")
                        await asyncio.sleep(60)
            except Exception as e:
                print(f"❌ Login error: {e}")
        
        # 2. Navigate to conversations
        print("\n📍 Step 2: Checking Conversations...")
        conversations_url = f"https://app.gohighlevel.com/v2/location/{GHL_LOCATION_ID}/conversations/conversations"
        await page.goto(conversations_url, wait_until="networkidle")
        await asyncio.sleep(3)
        
        # Take screenshot
        screenshot_path = "ghl_conversations.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # 3. Check for recent emails to our targets
        print("\n📍 Step 3: Searching for target emails...")
        targets = ["craig@scottsair.com", "allisa.sommers@airprosusa.com", "tony@thelakelandac.com"]
        
        for target in targets:
            print(f"  🔍 Searching for: {target}")
            try:
                # Look for search box and search
                search_box = await page.query_selector('input[placeholder*="Search"]')
                if search_box:
                    await search_box.fill(target)
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(2)
            except Exception as e:
                print(f"  ⚠️ Search failed: {e}")
        
        # 4. Navigate to Automation/Workflows
        print("\n📍 Step 4: Checking Workflows...")
        workflows_url = f"https://app.gohighlevel.com/v2/location/{GHL_LOCATION_ID}/workflows"
        await page.goto(workflows_url, wait_until="networkidle")
        await asyncio.sleep(3)
        
        # Take screenshot
        screenshot_path = "ghl_workflows.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Look for email-related workflows
        content = await page.content()
        if "email" in content.lower():
            print("✅ Found email-related workflow(s)")
        
        # Check for draft/inactive workflows
        if "draft" in content.lower():
            print("⚠️ WARNING: Found DRAFT workflows!")
        
        # 5. Check Settings > Webhooks
        print("\n📍 Step 5: Checking Webhook Settings...")
        settings_url = f"https://app.gohighlevel.com/v2/location/{GHL_LOCATION_ID}/settings/webhooks"
        await page.goto(settings_url, wait_until="networkidle")
        await asyncio.sleep(3)
        
        # Take screenshot
        screenshot_path = "ghl_webhooks.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        print("\n" + "=" * 60)
        print("INVESTIGATION COMPLETE")
        print("=" * 60)
        print("Check the screenshots in the current directory:")
        print("  - ghl_conversations.png")
        print("  - ghl_workflows.png")
        print("  - ghl_webhooks.png")
        
        # Keep browser open for manual inspection
        print("\n⏳ Browser will stay open for 30 seconds for manual inspection...")
        await asyncio.sleep(30)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(investigate_ghl())
