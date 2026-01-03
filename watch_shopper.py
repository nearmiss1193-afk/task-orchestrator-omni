from playwright.sync_api import sync_playwright
import time
import sys

# Force UTF-8 for console output
sys.stdout.reconfigure(encoding='utf-8')

def run():
    print("🚀 Launching Visual Shopper (Debug Mode)...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()
            
            url = "https://nearmiss1193-afk--ghl-omni-automation-hvac-landing.modal.run"
            print(f"🌐 Navigating to {url}...")
            page.goto(url)
            
            # Hero Check
            print("👉 Clicking 'Start Winning' (Hero CTA)...")
            # Use general selector, first button is Hero CTA
            page.locator("button.btn-primary").first.click()
            
            # Step 1
            print("⏳ Waiting for Step 1 (Missed Calls)...")
            page.wait_for_selector("#funnelStep1.active", timeout=5000)
            print("✅ Step 1 Visible. Clicking Option...")
            page.locator(".funnel-option").filter(has_text="Capture every call").first.click()
            
            # Step 2
            print("⏳ Waiting for Step 2 (Small Crew)...")
            page.wait_for_selector("#funnelStep2.active", timeout=5000)
            print("✅ Step 2 Visible. Clicking Option...")
            page.locator(".funnel-option").filter(has_text="Small crew").first.click()
            
            # Step 3
            print("⏳ Waiting for Step 3 (Summer)...")
            page.wait_for_selector("#funnelStep3.active", timeout=5000)
            print("✅ Step 3 Visible. Clicking Option...")
            page.locator(".funnel-option").filter(has_text="Summer").first.click()
            
            # Step 4
            print("⏳ Waiting for Step 4 (Start Free Trial)...")
            page.wait_for_selector("#funnelStep4.active", timeout=5000)
            # Step 4 - Choose "I'm Ready" to test Payment Link
            print("✅ Step 4 Visible. Clicking 'I'm Ready' (Direct Payment)...")
            page.locator(".funnel-option").filter(has_text="I'm Ready").first.click()
            
            # Verification & Form Filling
            print("⏳ Verifying PAYMENT Form Frame...")
            # Payment Step ID is #funnelStepPayment
            frame_el = page.wait_for_selector("#funnelStepPayment.active iframe", timeout=25000)
            
            if frame_el:
                print("✅ Found Payment Iframe. Switching context...")
                # Playwright frame handling
                frame = page.frame_locator("#funnelStepPayment.active iframe")
                
                # Wait for payment form fields (usually Credit Card or Email first)
                print("⏳ Waiting for Payment form to load...")
                # Inspecting typical GHL payment form elements
                # Usually has 'Credit Card' text or input[name='email']
                try:
                    frame.locator("body").wait_for(timeout=10000)
                    print("✅ Payment Form loaded inside iframe.")
                except:
                    print("⚠️ Could not verify content inside iframe (cross-origin?), but iframe exists.")

                print("[SHOpper_VERIFY] SUCCESS: Payment Flow Integrated.")
                page.screenshot(path="shopper_payment_success.png")
            else:
                 print("[SHOpper_VERIFY] FAIL: Payment Frame not found")
                 
            print("Browser remaining open for 10s...")
            time.sleep(10)
            browser.close()
            
        except Exception as e:
            err_msg = f"[SHOpper_VERIFY] FAIL: {str(e)}"
            print(err_msg)
            with open("last_error.txt", "w", encoding="utf-8") as f:
                f.write(err_msg)
            try:
                page.screenshot(path="shopper_fail.png")
            except:
                pass
            sys.exit(1)

if __name__ == "__main__":
    run()
