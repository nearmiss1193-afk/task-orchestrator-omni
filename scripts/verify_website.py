"""Playwright verification script for aiserviceco.com"""
import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SITE_URL = "https://aiserviceco-empire.netlify.app"
SCREENSHOT_DIR = "verification_screenshots"

async def verify_website():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    results = {
        "url": SITE_URL,
        "timestamp": timestamp,
        "checks": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        try:
            # Navigate to site
            print(f"Navigating to {SITE_URL}...")
            await page.goto(SITE_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Screenshot 1: Homepage
            await page.screenshot(path=f"{SCREENSHOT_DIR}/01_homepage_{timestamp}.png", full_page=False)
            print("✅ Screenshot: Homepage")
            
            # Check: Vapi Widget exists
            vapi_widget = await page.locator('[class*="vapi"], [id*="vapi"], [data-vapi]').count()
            if vapi_widget > 0:
                results["checks"].append({"name": "Vapi Widget", "status": "PASS", "count": vapi_widget})
                print(f"✅ Vapi Widget found: {vapi_widget} elements")
            else:
                # Check for the pill button
                pill = await page.locator('button:has-text("Talk"), [class*="pill"]').count()
                results["checks"].append({"name": "Vapi Widget", "status": "CHECK", "count": pill})
                print(f"⚠️ Vapi Widget check: pill buttons = {pill}")
            
            # Scroll to contact section
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.7)")
            await page.wait_for_timeout(2000)
            
            # Screenshot 2: Contact section
            await page.screenshot(path=f"{SCREENSHOT_DIR}/02_contact_{timestamp}.png", full_page=False)
            print("✅ Screenshot: Contact section")
            
            # Check: GHL Form iframe
            form_iframe = await page.locator('iframe[src*="links.aiserviceco.com"]').count()
            if form_iframe > 0:
                results["checks"].append({"name": "GHL Form", "status": "PASS", "count": form_iframe})
                print(f"✅ GHL Form iframe found: {form_iframe}")
            else:
                # Check for any form
                any_form = await page.locator('iframe, form, [class*="form"]').count()
                results["checks"].append({"name": "GHL Form", "status": "CHECK", "count": any_form})
                print(f"⚠️ GHL Form check: {any_form} form elements")
            
            # Check: Calendar iframe
            calendar_iframe = await page.locator('iframe[src*="YWQcHuXXznQEQa7LAWeB"]').count()
            if calendar_iframe > 0:
                results["checks"].append({"name": "GHL Calendar", "status": "PASS", "count": calendar_iframe})
                print(f"✅ GHL Calendar iframe found: {calendar_iframe}")
            else:
                cal_check = await page.locator('iframe[src*="calendar"], iframe[src*="booking"]').count()
                results["checks"].append({"name": "GHL Calendar", "status": "CHECK", "count": cal_check})
                print(f"⚠️ GHL Calendar check: {cal_check} calendar elements")
            
            # Check: Talk to Sarah button
            sarah_button = await page.locator('a:has-text("Talk to Sarah"), button:has-text("Sarah")').count()
            results["checks"].append({"name": "Sarah Button", "status": "FOUND" if sarah_button > 0 else "NOT FOUND", "count": sarah_button})
            print(f"{'✅' if sarah_button > 0 else '❌'} Sarah Button: {sarah_button}")
            
            # Check: All links work (no 404)
            links = await page.locator('a[href]').all()
            broken_links = []
            for link in links[:10]:  # Check first 10 links
                href = await link.get_attribute('href')
                if href and href.startswith('http'):
                    try:
                        response = await page.request.head(href, timeout=5000)
                        if response.status >= 400:
                            broken_links.append({"url": href, "status": response.status})
                    except:
                        pass
            
            results["checks"].append({"name": "Broken Links", "status": "PASS" if len(broken_links) == 0 else "FAIL", "broken": broken_links})
            print(f"{'✅' if len(broken_links) == 0 else '❌'} Broken Links: {len(broken_links)}")
            
            # Full page screenshot
            await page.screenshot(path=f"{SCREENSHOT_DIR}/03_fullpage_{timestamp}.png", full_page=True)
            print("✅ Screenshot: Full page")
            
            # Check console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            await page.reload()
            await page.wait_for_timeout(2000)
            
            results["checks"].append({"name": "Console Errors", "status": "PASS" if len(console_errors) == 0 else "WARN", "errors": console_errors[:5]})
            print(f"{'✅' if len(console_errors) == 0 else '⚠️'} Console Errors: {len(console_errors)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results["error"] = str(e)
            await page.screenshot(path=f"{SCREENSHOT_DIR}/error_{timestamp}.png")
        
        await browser.close()
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    passed = sum(1 for c in results["checks"] if c.get("status") == "PASS")
    total = len(results["checks"])
    print(f"Passed: {passed}/{total}")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}/")
    
    return results

if __name__ == "__main__":
    asyncio.run(verify_website())
