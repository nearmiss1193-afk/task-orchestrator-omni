import modal
import os
from playwright.sync_api import sync_playwright

app = modal.App("ghl-debug-session")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("playwright==1.40.0", "fastapi", "python-dotenv")
    .run_commands(
        "apt-get update",
        "apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libxkbcommon0 libgtk-3-0 libdrm2 libgbm1 libasound2 git",
        "playwright install chromium"
    )
    # No mounts needed, script is self-contained
)
# Note: if modules is still big, I might need to target specific files. 
# But let's assume 'modules' code is small enough compared to root.

import dotenv
dotenv.load_dotenv()

ghl_secrets = modal.Secret.from_dict({
    "GHL_EMAIL": os.environ.get("GHL_EMAIL"),
    "GHL_PASSWORD": os.environ.get("GHL_PASSWORD"),
})

debug_vol = modal.Volume.from_name("ghl-debug-vol", create_if_missing=True)

@app.function(image=image, secrets=[ghl_secrets], volumes={"/data": debug_vol}, timeout=900)
@modal.web_endpoint(method="GET")
def run_backend_setup():
    try:
        print("🎥 Starting Video Recording of Product Setup...", flush=True)
        
        products = [
            {"title": "Starter Plan", "price": "97"},
            {"title": "Growth Partner", "price": "297"},
            {"title": "Dominance", "price": "497"}
        ]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(record_video_dir="/data/videos/")
            page = context.new_page()
            page.set_default_timeout(60000)
            
            email = os.environ["GHL_EMAIL"]
            password = os.environ["GHL_PASSWORD"]
            
            try:
                print(f"🔑 Logging in as {email}...", flush=True)
                page.goto("https://app.gohighlevel.com/", wait_until="networkidle")
                page.fill("input[type='email']", email)
                page.fill("input[type='password']", password)
                page.click("button:has-text('Sign in')")
                
                # Robust Login
                try:
                    page.wait_for_url("**/dashboard", timeout=90000)
                except:
                    print("⚠️ Dashboard URL not reached, checking for blockers...")
                    page.screenshot(path="/data/login_stuck.png")

                print("✅ Login Success.", flush=True)
                
                sub_account_id = "RnK4QjX0oDcqtWw0VyLr"
                target_url = f"https://app.gohighlevel.com/v2/location/{sub_account_id}/payments/products"
                print(f"💳 Navigating to {target_url}...", flush=True)
                page.goto(target_url, wait_until="networkidle")
                page.wait_for_load_state("networkidle")
                
                # Just take a screenshot/video of the list to prove we are there
                page.wait_for_timeout(5000)
                print("📸 Taking Proof Screenshot...", flush=True)
                page.screenshot(path="/data/products_list_proof.png")
                
                for prod in products:
                    print(f"🛠 Attempting to Create {prod['title']}...", flush=True)
                    # Try to click create
                    try:
                        page.click("button:has-text('Create Product')", timeout=5000)
                        page.wait_for_timeout(2000)
                        page.screenshot(path=f"/data/product_modal_{prod['title']}.png")
                        # If we got here, grand. If not, catching exception.
                    except Exception as ex:
                        print(f"⚠️ Create Button Failed for {prod['title']}: {ex}", flush=True)
                
            except Exception as e:
                print(f"❌ Automation Error: {e}", flush=True)
                page.screenshot(path="/data/error_state.png")
                return {"status": "error", "message": str(e)}
            finally:
                path = page.video.path()
                context.close()
                browser.close()
                print(f"📼 Video Saved to: {path}", flush=True)
                return {"status": "success", "video_path": path}
    except Exception as e:
        return {"status": "fatal_error", "message": str(e)}

@app.function(image=image, volumes={"/data": debug_vol})
def test_vol():
    import os
    print("Testing Volume Write...", flush=True)
    with open("/data/debug.txt", "w") as f:
        f.write("Debug Active")
    print(f"Written. Files: {os.listdir('/data')}", flush=True)
