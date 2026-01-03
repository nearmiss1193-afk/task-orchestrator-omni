
import os
import time
from playwright.sync_api import sync_playwright

def setup_products():
    """
    Automates the creation of Stripe Products in GHL.
    Focus: Starter ($97), Growth ($297), Dominance ($497).
    Uses the SYSTEM Chrome Profile (User Data) to ensure login state.
    """
    import shutil
    
    email = os.environ.get("GHL_EMAIL")
    password = os.environ.get("GHL_PASSWORD")
    
    # 1. Locate System Profile
    # Typical: C:\Users\<User>\AppData\Local\Google\Chrome\User Data
    user_home = os.path.expanduser("~")
    system_profile_path = os.path.join(user_home, "AppData", "Local", "Google", "Chrome", "User Data")
    
    if not os.path.exists(system_profile_path):
        print(f"⚠️ System profile not found at {system_profile_path}. Falling back to local.")
        user_data_dir = os.path.join(os.getcwd(), ".ghl_browser_data")
    else:
        print(f"📂 Detected System Profile: {system_profile_path}")
        user_data_dir = system_profile_path

    # Verify existing products logic...
    products = [
        {"title": "Starter Plan", "price": "97"},
        {"title": "Growth Partner", "price": "297"},
        {"title": "Dominance", "price": "497"}
    ]

    with sync_playwright() as p:
        executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(executable_path):
            executable_path = None
        
        print(f"🚀 Launching Chrome with Profile: {user_data_dir}")
        print("⚠️ NOTE: If Chrome is open, this might fail or open a new window in the existing session.")
        
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                executable_path=executable_path,
                channel="chrome" if executable_path else None,
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
            )
        except Exception as e:
            print(f"❌ Could not launch with System Profile (likely locked): {e}")
            print("👉 Please CLOSE ALL Chrome windows and try again.")
            print("   Alternatively, I can try to copy your profile cookies to a temp folder (risky).")
            return

        page = browser.pages[0]
        
        print("🔑 Navigating to GHL...")
        page.goto("https://app.gohighlevel.com/")
        
        try:
            page.wait_for_url("**/dashboard", timeout=8000)
            print("✅ Detected Dashboard! Logged in as User.")
        except:
             print("⚠️ Not on dashboard yet. Please Log In manually if needed.")
             try:
                page.wait_for_url("**/dashboard", timeout=300000)
                print("✅ Dashboard access confirmed.")
             except:
                print("❌ Login timed out.")
                return

        # Check Agency
        if "agency" in page.url:
             print("⚠️ Agency View. Please switch to sub-account.")
             page.wait_for_url(lambda u: "location" in u, timeout=300000)

        # Go to Products
        print("💳 Navigating to Products...")
        products_url = "https://app.gohighlevel.com/v2/payments/products"
        if products_url not in page.url:
            page.goto(products_url)
        
        time.sleep(5)
        
        for prod in products:
            if page.get_by_text(prod['title'], exact=False).count() > 0:
                print(f"✅ {prod['title']} exists.")
                continue

            print(f"🛠 Creating {prod['title']}...")
            try:
                page.get_by_text("Create Product", exact=False).click(timeout=3000)
            except:
                 try: page.click("a[href*='new']", timeout=2000)
                 except: pass

            try:
                page.get_by_placeholder("Product Name").fill(prod['title'])
                page.get_by_placeholder("Amount").fill(prod['price'])
                page.get_by_text("Save", exact=False).click()
                time.sleep(2)
                print(f"✅ {prod['title']} Created.")
            except:
                print(f"❌ Failed to create {prod['title']}")

        print("🏁 Done.")
        browser.close()

if __name__ == "__main__":
    setup_products()
