
import asyncio
import os
import shutil
from playwright.async_api import async_playwright

async def audit_session():
    primary_profile_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    target_data_dir = os.path.join(os.getcwd(), ".ghl_audit_profile")
    
    print(f"[AUDIT] Attempting session audit...")
    try:
        if os.path.exists(target_data_dir): shutil.rmtree(target_data_dir)
        os.makedirs(target_data_dir, exist_ok=True)
        default_profile = os.path.join(primary_profile_path, "Default")
        if os.path.exists(default_profile):
            target_default = os.path.join(target_data_dir, "Default")
            os.makedirs(target_default, exist_ok=True)
            for f in ["Cookies", "Local Storage", "Session Storage"]:
                src = os.path.join(default_profile, f)
                dst = os.path.join(target_default, f)
                if os.path.exists(src):
                    try:
                        if os.path.isdir(src): shutil.copytree(src, dst, dirs_exist_ok=True)
                        else: shutil.copy2(src, dst)
                    except: pass
    except: pass

    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                target_data_dir,
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = await context.new_page()
            
            print("[AUDIT] Navigating to GHL Dashboard...")
            await page.goto("https://app.gohighlevel.com/v2/location", wait_until="load", timeout=120000)
            await asyncio.sleep(20)
            
            current_url = page.url
            print(f"[AUDIT] Initialized URL: {current_url}")
            
            if "location" in current_url:
                location_id = current_url.split("location/")[1].split("/")[0]
                print(f"[AUDIT] ✅ DETECTED LOCATION ID: {location_id}")
                
                # Navigate to workflows
                workflow_url = f"https://app.gohighlevel.com/v2/location/{location_id}/automation/workflows"
                print(f"[AUDIT] Scanning workflows at {workflow_url}...")
                await page.goto(workflow_url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(10)
                
                workflows = await page.evaluate("""() => {
                    const rows = Array.from(document.querySelectorAll('a[href*="workflow/"]'));
                    return rows.map(r => ({ name: r.textContent.trim(), id: r.href.split('workflow/')[1] }));
                }""")
                print(f"[AUDIT] FOUND WORKFLOWS: {workflows}")
            else:
                print("[AUDIT] ❌ NOT LOGGED IN or WRONG PAGE.")
            
            await page.screenshot(path="ghl_audit_state.png")
            await context.close()
        except Exception as e:
            print(f"[AUDIT] ❌ ERROR: {e}")
            await context.close()

if __name__ == "__main__":
    asyncio.run(audit_session())
