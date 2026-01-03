
import argparse
import sys

class GHLPageBuilder:
    """
    Constructs High-Fidelity HTML/Tailwind for GHL Funnel Steps (Code Editor).
    """
    
    def __init__(self):
        self.templates = {
            "hvac": {
                "headline": "Stop Losing AC Jobs to Missed Calls",
                "sub": "If you don't answer instantly, 70% of leads call the next guy. Fix it in 5 minutes.",
                "bg": "https://images.unsplash.com/photo-1581094794329-cd1361ddee2f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80",
                "cta": "Starts at $297/mo"
            },
            "roofer": {
                "headline": "Catch Every Storm Lead",
                "sub": "Your crew is on the roof. Your phone is ringing. Let AI answer it.",
                "bg": "https://images.unsplash.com/photo-1623190866774-88aa3807212d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80",
                "cta": "Get a Demo"
            },
            "generic": {
                "headline": "AI That Answers Your Phone",
                "sub": "Never miss a lead again. 24/7 Auto-Reply via SMS.",
                "bg": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80",
                "cta": "Start Trial"
            }
        }


    def build_code(self, niche="generic"):
        if niche.lower() == "hvac":
            try:
                from modules.web.hvac_landing import get_hvac_landing_html
                # Use known good links if available, otherwise placeholders that don't crash
                return get_hvac_landing_html(
                    calendly_url="https://calendly.com/aiserviceco/demo",
                    stripe_url="#" 
                )
            except ImportError:
                print("⚠️ Warning: modules.web.hvac_landing not found. Falling back to generic template.")
        
        data = self.templates.get(niche.lower(), self.templates["generic"])
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; overflow-x: hidden; }}
        .hero-bg {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: url('{data['bg']}');
            background-size: cover; background-position: center;
            animation: zoomEffect 20s infinite alternate;
            z-index: -1; filter: grayscale(100%) brightness(0.2); /* Black & White vibe */
        }}
        @keyframes zoomEffect {{ from {{ transform: scale(1); }} to {{ transform: scale(1.1); }} }}
        .glass-panel {{
            background: rgba(0, 0, 0, 0.6); /* Darker Glass */
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 0, 0, 0.3); /* Red Border Accent */
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        }}
    </style>
</head>
<body class="bg-black text-white min-h-screen flex items-center justify-center p-4">

    <div class="hero-bg"></div>

    <div class="glass-panel w-full max-w-4xl p-8 md:p-12 rounded-2xl text-center relative z-10">
        
        <div class="inline-block px-4 py-1 mb-6 text-xs tracking-widest text-red-500 uppercase bg-black rounded-full border border-red-600 font-bold">
            For {niche.capitalize()} Business Owners
        </div>
        
        <h1 class="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 text-white">
            {data['headline']} <span class="text-red-600">.</span>
        </h1>
        
        <p class="text-lg md:text-2xl text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
            {data['sub']}
        </p>

        <!-- CTA Area -->
        <div class="flex flex-col md:flex-row gap-6 justify-center items-center">
            <a href="#go" class="w-full md:w-auto px-8 py-4 bg-red-700 hover:bg-red-600 text-white font-bold rounded-none uppercase tracking-wider transition-transform transform hover:-translate-y-1 shadow-2xl border border-red-500">
                {data['cta']}
            </a>
            <span class="text-sm text-gray-400">No Credit Card Required</span>
        </div>

    </div>
</body>
</html>
"""
        return html

class GHLLauncher:
    """
    Automates the deployment of code to GHL via Playwright.
    """
    def __init__(self, headless=False):
        try:
            from playwright.sync_api import sync_playwright
            self.p = sync_playwright().start()
            self.browser = self.p.chromium.launch(headless=headless)
            self.page = self.browser.new_page()
            print("🚀 Browser Launched.")
        except ImportError:
            print("❌ Playwright not installed. Run 'pip install playwright && playwright install'.")
            sys.exit(1)

    def deploy(self, code, email, password, target_funnel="havac ai"):
        print("🔐 Logging into GoHighLevel...")
        self.page.goto("https://app.gohighlevel.com/")
        
        # Login Flow
        try:
            self.page.fill("input[type='email']", email)
            self.page.fill("input[type='password']", password)
            self.page.click("button[type='submit']")
            self.page.wait_for_url("**/location/**", timeout=60000)
            print("✅ Login Successful.")
        except Exception as e:
            print(f"❌ Login Failed: {e}")
            self.browser.close()
            return

        # Navigate to Funnels
        print("🧭 Navigating to Funnels...")
        curr_url = self.page.url
        if "/location/" in curr_url:
            base = curr_url.split("/dashboard")[0]
            if "/funnels" not in base:
                self.page.goto(f"{base}/funnels")
        
        time.sleep(5) # Allow SPA load
        
        # Select Target Funnel
        print(f"🔍 Searching for funnel: '{target_funnel}'...")
        try:
            # Type in search box if available (usually top left)
            self.page.fill("input[placeholder*='Search']", target_funnel)
            time.sleep(2)
            # Click the card that matches the text
            self.page.click(f".hl_funnel-card--name:has-text('{target_funnel}')", timeout=5000)
            print(f"✅ Found and clicked '{target_funnel}'")
        except:
            print(f"⚠️ Funnel '{target_funnel}' not found via search. Attempting absolute fallback match...")
            try:
                 self.page.click(f"text={target_funnel}", timeout=5000)
            except:
                 print(f"❌ Could not find funnel '{target_funnel}'. Aborting logic to prevent overwriting wrong funnel.")
                 # DUMP CURRENT HTML for Debugging
                 with open("ghl_debug_dump.html", "w") as f:
                     f.write(self.page.content())
                 print("📸 Saved debug dump to ghl_debug_dump.html")
                 self.browser.close()
                 return

        # Add New Step
        print("Steps: Adding Page...")
        try:
            self.page.click("button:has-text('Add New Step')")
            self.page.fill("input[placeholder='Name_Input']", "Landing Page")
            self.page.fill("input[placeholder='Path_Input']", "home")
            self.page.click("button:has-text('Create Funnel Step')")
            time.sleep(3)
        except:
            print("⚠️ Could not add step, assuming step exists.")

        # Create Checkout Step (User Requested Form)
        print("Steps: Ensuring '/checkout' step exists...")
        try:
            # Check if checkout step exists in list (logic varies by GHL version, simplifying to 'Add if fails')
            # For speed, we just try to add it. GHL usually handles duplicate paths by appending numbers.
            # ideally we check list.
            self.page.click("button:has-text('Add New Step')")
            self.page.fill("input[placeholder='Name_Input']", "Checkout")
            self.page.fill("input[placeholder='Path_Input']", "checkout")
            self.page.click("button:has-text('Create Funnel Step')")
            time.sleep(3)
            print("✅ Checkout Step /checkout Created.")
        except Exception as e:
           print(f"⚠️ Checkout step creation note: {e}")
        
        # Refocus on Landing Page to Edit
        try:
             self.page.click("div:has-text('Landing Page')") # Click back to home step
             time.sleep(2)
        except:
             pass

        # Open Editor
        print("✏️ Opening Editor...")
        try:
            self.page.click("text=Edit Page", timeout=10000)
            # Wait for GHL Editor heavyweight load
            self.page.wait_for_selector(".hl_page-creator--content", timeout=60000)
            time.sleep(5) # Let animations finish
        except Exception as e:
            print(f"❌ Editor Load Failed: {e}")
            self.browser.close()
            return

        # Inject Code (The Hard Part)
        print("💉 Injecting HTML Code...")
        try:
            # 1. Add Full Width Section
            # Note: Selectors are incredibly fragile in GHL. We use text and generic classes where possible.
            # Assuming prompt to "start from scratch" or empty page
            
            # Click 'Full Width' if it asks for layout
            if self.page.is_visible("text=Full Width"):
                self.page.click("text=Full Width")
            
            # Click 'Add Row' -> '1 Column'
            if self.page.is_visible("text=Add Row"):
                self.page.click("text=Add Row")
                self.page.click("text=1 Column")
                
            # Click 'Add Element'
            self.page.click("text=Add Element")
            self.page.fill("input[placeholder='Search Elements']", "html")
            self.page.click("text=Custom JS/HTML")
            
            # Click the element to open settings
            self.page.click(".c-custom-js-html") 
            self.page.click("button:has-text('Open Code Editor')")
            
            # Paste Code in Monaco/Ace Editor
            # Strategy: Click generic textarea or use keyboard
            self.page.click(".ace_editor") 
            # Select All + Delete
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")
            # Type/Paste (Paste is safer for large text)
            # self.page.keyboard.insert_text(code) # Too slow for big HTML
            
            # Evaluate JS to set value safely using JSON serialization
            import json
            safe_code = json.dumps(code)
            
            # Use a standard function wrapper to ensure scope safety
            js_hack = f"""
            var editor = ace.edit(document.querySelector('.ace_editor'));
            editor.setValue({safe_code});
            """
            self.page.evaluate(js_hack)
            
            # FORCE DIRTY STATE:
            self.page.click(".ace_editor")
            self.page.keyboard.type(" ")
            self.page.keyboard.press("Backspace")
            time.sleep(1)

            # TRY TO DISMISS BLOCKING BANNERS (Aggressive)
            try:
                # Common GHL Banner Close Buttons
                self.page.click(".banner-close", timeout=1000)
                self.page.click("[aria-label='Close']", timeout=1000)
                self.page.click(".n-banner__close", timeout=1000)
            except:
                pass
            
            # METHOD 1: KEYBOARD SHORTCUT
            print("⌨️ Attempting Ctrl+S...")
            self.page.keyboard.press("Control+s")
            time.sleep(2)
            
            # METHOD 2: EXPLICIT BUTTON CLICK
            print("💾 Clicking Save Button (Force)...")
            try:
                # Dump Header to debug selectors
                header_html = self.page.inner_html(".hl_header--controls")
                print(f"HEADER HTML: {header_html[:500]}...") # Log first 500 chars
                
                self.page.click("button:has-text('Save')", timeout=3000)
            except Exception as e:
                print(f"⚠️ Button Click Failed: {e}")

            # CRITICAL: VERIFY SAVE
            print("👀 Waiting for 'Saved' notification...")
            try:
                # Look for "Saved" or "Updates Saved" toast
                # GHL Toast class usually: .n-toast or .toast
                self.page.wait_for_selector("text=Saved", timeout=8000)
                print("✅ CONFIRMED: 'Saved' notification appeared.")
            except:
                print("❌ ERROR: Save notification did NOT appear. The Save likely failed.")
                self.save_screenshot("save_failed.png")
                raise Exception("Save Verification Failed - GHL did not confirm save.")
            
            self.save_screenshot("deploy_success.png")
            print("✅ Deployment Logic Complete.")
            
        except Exception as e:
            print(f"⚠️ GHL Editor Automation Limit Reached: {e}")
            self.save_screenshot("deploy_error.png")
            # If we dump the HTML, we can debug better
            # debug_dump ...
            print("👉 Please Paste the code manually.")
        
        self.browser.close()

    def save_screenshot(self, filename="debug.png"):
        """Captures what the bot sees."""
        try:
            path = f"/data/{filename}" # Save to Modal Volume if possible, or local
            self.page.screenshot(path=filename)
            print(f"📸 Screenshot saved to {filename}")
        except Exception as e:
            print(f"Could not save screenshot: {e}")

    def setup_products(self, products):
        """
        Navigates to Payments > Products and creates them.
        """
        print("💳 Navigating to Payments > Products...")
        # Force navigation via URL
        sub_account_id = "RnK4QjX0oDcqtWw0VyLr" # Extracted from user URL/Screenshots
        self.page.goto(f"https://app.gohighlevel.com/v2/location/{sub_account_id}/payments/products")
        time.sleep(5)
        
        self.save_screenshot("products_page_load.png")

        for prod in products:
            print(f"🛠 Creating Product: {prod['title']}...")
            try:
                # 1. Click Create Product
                self.page.click("button:has-text('Create Product')", timeout=5000)
                time.sleep(2)
                
                # 2. Fill Title
                # Selectors are guesses based on standard GHL inputs
                self.page.fill("input[placeholder='Product Name']", prod['title'])
                
                # 3. Fill Price (Might be in a 'Pricing' tab or step)
                # Assuming simple form for now. 
                # If complex, we need 'shopper' to map it. 
                # Trying generic filler:
                self.page.fill("input[placeholder='Amount']", prod['price'])
                
                # 4. Save
                self.page.click("button:has-text('Save')")
                time.sleep(3)
                print(f"✅ {prod['title']} Created.")
            except Exception as e:
                print(f"❌ Failed to create {prod['title']}: {e}")
                self.save_screenshot(f"product_fail_{prod['title']}.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GHL Page Builder Agent")
    parser.add_argument("--niche", type=str, default="generic", help="Target Niche (hvac, roofer)")
    parser.add_argument("--out", type=str, default="ghl_page_code.html", help="Output filename")
    parser.add_argument("--deploy", action="store_true", help="Attempt to auto-deploy via Playwright")
    parser.add_argument("--email", type=str, help="GHL Email")
    parser.add_argument("--password", type=str, help="GHL Password")
    
    args = parser.parse_args()
    
    builder = GHLPageBuilder()
    code = builder.build_code(args.niche)
    
    if args.deploy:
        if not args.email or not args.password:
            import os
            email = os.environ.get("GHL_EMAIL")
            password = os.environ.get("GHL_PASSWORD")
            if not email or not password:
                print("❌ --deploy requires --email and --password (or env vars).")
                sys.exit(1)
        else:
            email, password = args.email, args.password
            
        launcher = GHLLauncher(headless=False)
        launcher.deploy(code, email, password)
    else:
        with open(args.out, "w") as f:
            f.write(code)
            
        print(f"✅ GHL Code Generated: {args.out}")
        print(f"👉 Copy content of {args.out} into your GHL 'Custom HTML' element.")
