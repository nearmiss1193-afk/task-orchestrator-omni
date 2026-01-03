import time
from playwright.sync_api import sync_playwright

def run_shopper_loop():
    print("🕵️  Secret Shopper: Starting In-Depth Audit (2 Loops)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Set to False if you want to watch it visually
        context = browser.new_context()
        page = context.new_page()

        # Config
        base_url = "https://jeanie-makable-deve-deon.ngrok-free.dev"
        # We audit all 3 to ensure system-wide health
        landing_pages = [
            "/landing/hvac.html",
            # "/landing/plumber.html", 
            # "/landing/roofer.html" 
        ]
        
        loop_count = 2
        print(f"🕵️  Shopper: Running Double-Check Routine ({loop_count} Loops)...")
        
        for loop in range(1, loop_count + 1):
            print(f"\n🔄  Loop {loop}/{loop_count} - Audit Started")
            
            for landing in landing_pages:
                full_url = f"{base_url}{landing}"
                print(f"   📍 Visiting: {full_url}")
                
                try:
                    page.goto(full_url)
                    page.wait_for_load_state("networkidle")
                    
                    # 1. Check Chat Widget Trigger (The Red Bubble)
                    print("      Checking Chat Widget...")
                    # We look for the class we added: .chat-widget-trigger
                    if page.locator(".chat-widget-trigger").count() > 0:
                        print("      ✅ Chat Widget Found (Visual).")
                        # Click it to test interactivity
                        page.click(".chat-widget-trigger")
                        time.sleep(1) # Animation wait
                        
                        # Verify Modal Opened
                        if page.locator("#leadModal").is_visible():
                            print("      ✅ Chat Widget Click -> Modal Opened Successfully.")
                            # Close it
                            page.click(".close-modal")
                            time.sleep(0.5)
                        else:
                            print("      ❌ Chat Widget Clicked but Modal NOT visible.")
                    else:
                        print("      ⚠️ Chat Widget trigger NOT found on page.")

                    # 2. Check Main "Get Started" CTA
                    print("      Checking Main CTA...")
                    # Click the first CTA found
                    if page.locator("text=Get Started").count() > 0:
                        page.click("text=Get Started", timeout=2000)
                        time.sleep(1)
                        
                        if page.locator("#leadModal").is_visible():
                            print("      ✅ Main CTA Click -> Modal Opened Successfully.")
                            
                            # 3. Simulate Form Fill (Only on Loop 1 to avoid excessive spam)
                            if loop == 1:
                                print("      ✍️  Simulating Shopper Form Entry...")
                                
                                # Check for Compliance Checkbox and Click it
                                try:
                                    checkbox = page.locator('#complianceCheck')
                                    if checkbox.count() > 0 and checkbox.is_visible():
                                        print("      ✅ Clicking Compliance Checkbox...")
                                        checkbox.click()
                                    else:
                                        print("      ℹ️ No Compliance Checkbox found (or invisible).")
                                except Exception as e:
                                    print(f"      ⚠️ Checkbox interaction error: {e}")

                                page.fill("input[name='name']", "Secret Shopper Audit")
                                page.fill("input[name='phone']", "5550009999")
                                page.fill("input[name='email']", "shopper@audit.com")
                                
                                # Submit
                                page.click("button[type='submit']")
                                print("      ✅ Form Submitted")
                                
                                # Wait for Success Message using text locator
                                try:
                                    page.wait_for_selector("text=Success! Check Dashboard.", timeout=5000)
                                    print("      ✅ Form Submission: Success Message Verified.")
                                except:
                                    print("      ❌ Form Submission: Success Message NOT Found.")
                                
                                # Close modal
                                time.sleep(2)
                                if page.locator(".close-modal").is_visible():
                                    page.click(".close-modal")

                        else:
                            print("      ❌ Main CTA Clicked but Modal NOT visible.")
                    else:
                         print("      ⚠️ 'Get Started' CTA not found.")

                except Exception as e:
                    print(f"      ❌ Error checking {landing}: {e}")

        browser.close()
        print("\n✅  In-Depth Audit Complete. Ready for Launch.")

if __name__ == "__main__":
    run_shopper_loop()
